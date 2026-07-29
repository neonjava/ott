// core/src/job/mod.rs
use serde::{Deserialize, Serialize};
use std::collections::{BinaryHeap, HashMap};
use std::cmp::Ordering;
use uuid::Uuid;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum JobStatus {
    Queued,
    Running,
    Completed,
    Failed,
    Cancelled,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Job {
    pub id: String,
    pub name: String,
    pub priority: u32,
    pub dependencies: Vec<String>,
    pub status: JobStatus,
    pub progress_pct: f32,
    pub retry_count: u32,
    pub max_retries: u32,
    pub assigned_gpu: Option<u32>,
}

impl PartialEq for Job {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}

impl Eq for Job {}

impl Ord for Job {
    fn cmp(&self, other: &Self) -> Ordering {
        self.priority.cmp(&other.priority)
    }
}

impl PartialOrd for Job {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

#[derive(Debug, Default)]
pub struct JobScheduler {
    pub jobs: HashMap<String, Job>,
    pub queue: BinaryHeap<Job>,
}

impl JobScheduler {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn submit_job(&mut self, name: &str, priority: u32, dependencies: Vec<String>) -> String {
        let id = Uuid::new_v4().to_string();
        let job = Job {
            id: id.clone(),
            name: name.to_string(),
            priority,
            dependencies,
            status: JobStatus::Queued,
            progress_pct: 0.0,
            retry_count: 0,
            max_retries: 3,
            assigned_gpu: None,
        };

        self.jobs.insert(id.clone(), job.clone());
        self.queue.push(job);
        id
    }

    pub fn pop_next_runnable_job(&mut self) -> Option<Job> {
        let mut temp_stack = Vec::new();
        let mut selected = None;

        while let Some(job) = self.queue.pop() {
            let deps_met = job.dependencies.iter().all(|dep_id| {
                self.jobs.get(dep_id).map_or(false, |j| j.status == JobStatus::Completed)
            });

            if deps_met {
                selected = Some(job);
                break;
            } else {
                temp_stack.push(job);
            }
        }

        for j in temp_stack {
            self.queue.push(j);
        }

        if let Some(ref mut job) = selected {
            job.status = JobStatus::Running;
            if let Some(stored) = self.jobs.get_mut(&job.id) {
                stored.status = JobStatus::Running;
            }
        }

        selected
    }

    pub fn update_progress(&mut self, job_id: &str, progress_pct: f32) -> bool {
        if let Some(job) = self.jobs.get_mut(job_id) {
            job.progress_pct = progress_pct;
            if progress_pct >= 100.0 {
                job.status = JobStatus::Completed;
            }
            true
        } else {
            false
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_job_scheduler_priority_and_dependencies() {
        let mut scheduler = JobScheduler::new();
        let job1 = scheduler.submit_job("Low Priority Prep", 10, vec![]);
        let job2 = scheduler.submit_job("High Priority Render", 100, vec![job1.clone()]);

        let popped1 = scheduler.pop_next_runnable_job().unwrap();
        assert_eq!(popped1.id, job1);

        scheduler.update_progress(&job1, 100.0);

        let popped2 = scheduler.pop_next_runnable_job().unwrap();
        assert_eq!(popped2.id, job2);
    }
}
