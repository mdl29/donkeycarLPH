/**
 * Get the duration of a job, prints a warning and returns 0 if failed.
 * @param {Job} job - the job to take the duration of
 * @return {Number} - the duration in seconds
 */
export function getJobDuration (job) {
  try {
    const params = JSON.parse(job.parameters)
    let driveTime = parseInt(params.drive_time)
    if (isNaN(driveTime)) {
      driveTime = 0
    }

    if (typeof job.next_job_details === 'string') {
      const nextJob = JSON.parse(job.next_job_details)
      return driveTime + getJobDuration(nextJob)
    } else {
      return driveTime
    }
  } catch (e) {
    console.warn('Error when reading job duration, defaulting to 0s', e)
    return 0
  }
}

/**
 * Compute the wait time for a job (given perfect conditions)
 * @method
 * @param {Number[]} prev - duration of the jobs that are to be run before
 * @param {Number} workers - the number of workers
 * @return {Number} wait time in seconds, -1 means an unknown/infinite wait
*/
export function getJobWaitTime (prev, workers) {
  // Infinite/Unknown wait time if no worker are availible
  if (workers === 0) return -1
  // An array with the time spent on each workers
  const wait = new Array(workers).fill(0)
  while (prev.length > 0) {
    const batch = prev.splice(0, workers)
    batch.forEach((v, i) => {
      wait[i] += v
    })
    // Sort because the first job in prev should go the to first available worker
    // (the one with the least wait)
    wait.sort((a, b) => a > b)
  }
  // wait is sorted, so this is the min
  return wait[0]
}
