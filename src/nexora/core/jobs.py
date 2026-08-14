from nexora.models.job import Job, JobStatus


class JobBoard:
    """Provides jobs available in the simulated world."""

    def __init__(self, jobs: list[Job] | None = None) -> None:
        self._jobs = jobs or []

    def add(self, job: Job) -> None:
        """Add a job to the board."""

        if any(existing.id == job.id for existing in self._jobs):
            raise ValueError(f"Job already exists: {job.id}")

        self._jobs.append(job)

    def available(self) -> list[Job]:
        """Return all currently open jobs."""

        return [job for job in self._jobs if job.status == JobStatus.OPEN]

    def get(self, job_id: str) -> Job:
        """Return a job by ID."""

        for job in self._jobs:
            if job.id == job_id:
                return job

        raise KeyError(f"Unknown job: {job_id}")

    def complete(self, job_id: str) -> Job:
        """Mark a job as completed."""

        job = self.get(job_id)

        if job.status == JobStatus.COMPLETED:
            raise ValueError(f"Job is already completed: {job_id}")

        job.status = JobStatus.COMPLETED

        return job
