// why are we using 2 wide identation again ?

export function getJobDuration(job) {
  try {
    const params = JSON.parse(job.parameters);
    if (typeof job.next_job_details === 'string') {
      const next_job = JSON.parse(job.next_job_details);
      return parseInt(params.drive_time) + getJobDuration(next_job);
    } else {
      return parseInt(params.drive_time);
    }
  } catch(_) {
    return 0;
  }
}

/**
 * Compute the wait time for a job (given perfect conditions)
 * @method
 * @param {Number[]} prev - duration of the jobs that are to be run before
 * @param {Number} workers - the number of workers
 * @return {Number} wait time in seconds
*/
export function getJobWaitTime(prev, workers) {
  // An array with the time spent on each workers
  const wait = new Array(workers).fill(0);
  while (prev.length > 0) {
    const batch = prev.splice(0, workers);
    batch.forEach((v, i) => {
      wait[i] += v;
    })
    // Sort because the first job in prev should go the to first available worker
    // (the one with the least wait)
    wait.sort((a, b) => a > b);
  }
  // wait is sorted, so this is the min
  return wait[0];
}
