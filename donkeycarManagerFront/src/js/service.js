/**
 * @author Yannis Malgorn <yannismalgorn@gmail.com>
 * @see {@link https://github.com/mdl29/donkeycarLPH|GitHub}
 * @requires module:axios/axios
 */

import axios from 'axios'

/**
 * @typedef {Object} Player
 * @property {string} player_pseudo - Player pseudo
 * @property {string} register_datetime - Register Datetime
 * @property {int} player_id - Player Id
 */

/**
 * @typedef {Object} DrivingWaitingQueue
 * @property {int} player_id - Player Id
 * @property {int} rank - Player rank
 * @property {string} register_datetime - Start waiting Datetime
 */

export default class DonkeycarManagerService {
  static get ip () {
    return '192.168.20.42'
  }

  /**
  *
  * @constructor
  * @param {string} apiUrl - api url, eg: http://localhost:5000/api
  */
  constructor (apiUrl) {
    this.apiUrl = apiUrl
    this.players = new Map()
    this.drivingWaitingQueue = new Map()
  }

  //                               PLAYERS FUNCTIONS

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @param {string} pseudo - New player
  * @returns {Promise} -
  */
  async addPlayerToDatabase (pseudo) {
    const response = await axios.post(this.apiUrl + '/players', {
      player_pseudo: pseudo
    })
    return response.data.player_id
  }

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @param {int} playerId - player Id , e.g: 0
  * @returns {Promise} - all player information
  */
  async getPlayer (playerId) {
    const response = await axios.get(this.apiUrl + '/players/' + String(playerId))
    return response.data
  }

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @param {int} playerId - player Id , e.g: 0
  * @returns {Promise} - all player information
  */
  async getPlayerByPseudo (pseudo) {
    const response = await axios.get(this.apiUrl + '/players/?player_pseudo=' + String(pseudo) + '&skip=0&limit=100')
    return response.data
  }

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @returns {Promise} - all player information
  */
  async getAllPlayers () {
    const response = await axios.get(this.apiUrl + '/players/')
    return response.data
  }

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @param {Boolean} rank - sorted by rank or not
  * @param {int} skip - first player , e.g: 0
  * @param {int} limit - last player, e.g: 20
  * @returns {Promise} - all player information
  */
  async getDrivingWaitingQueue (rank, skip, limit) {
    const response = await axios.get(this.apiUrl + '/jobs/?by_rank=' + rank + '&skip=' + String(skip) + '&limit=' + String(limit) + '&worker_type=CAR&job_states=WAITING')
    return response.data
  }

  /**
  * @async
  * @augments donkeycarManagerService
  * @param {string} pseudo - pseudo of the new player
  * @returns {Promise} - all player information
  */
  async createPlayer (pseudo) {
    const response = await axios.post(this.apiUrl + '/players', {
      player_pseudo: pseudo
    })
    return response.data
  }

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @param {int} playerId - id of the player
  * @param {int} afterId - id of previous player
  * @returns {Promise} - all player information
  */
  async moveAfter (playerId, afterId) {
    const response = await axios.post(this.apiUrl + '/jobs/' + String(playerId) + '/move_after', {
      after_job_id: afterId
    })
    return response.data
  }

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @param {int} playerId - id of the player
  * @param {int} beforeId - id of previous player
  * @returns {Promise} - all player information
  */
  async moveBefore (playerId, beforeId) {
    const response = await axios.post(this.apiUrl + '/jobs/' + String(playerId) + '/move_before', {
      before_job_id: beforeId
    })
    return response.data
  }

  /**
   *
   * @async
   * @augments ScratchyService
   * @param {string} pseudo - player pseudo
   * @returns {Promise}
   */
  async updatePlayerPseudo (player, Newpseudo) {
    const response = await axios.put(this.apiUrl + '/players/' + String(player.player_id), {
      player_pseudo: Newpseudo,
      register_datetime: player.register_datetime,
      player_id: player.player_id
    })
    return response.data
  }

  /*                     CAR SERVICE              */

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @param {int} skip - first player , e.g: 0
  * @param {int} limit - last player, e.g: 20
  * @returns {Promise} - all player information
  */
  async getCars (skip, limit) {
    const response = await axios.get(this.apiUrl + '/cars/?skip=' + String(skip) + '&limit=' + String(limit))
    return response.data
  }

  /**
   *
   * @async
   * @augments donkeycarManagerService
   * @param {Array} Car - current car
   * @param {string} stage - current stage
   * @param {int} playerId - id of player in car
   * @returns {Promise}
   */
  async updateCar (car, stage, playerID) {
    const response = await axios.put(this.apiUrl + '/cars/' + car.name, {
      name: car.name,
      ip: car.ip,
      color: car.color,
      current_stage: stage,
      current_player_id: playerID,
      current_race_id: car.current_race_id,
      race: car.race,
      worker_id: car.worker_id
    })
    return response.data
  }

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @param {int} skip - first player , e.g: 0
  * @param {int} limit - last player, e.g: 20
  * @returns {Promise} - all player information
  */
  async fetchRaces (skip, limit) {
    const response = await axios.get(this.apiUrl + '/races/?skip=' + String(skip) + '&limit=' + String(limit))
    return response.data
  }

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @param {int} playerId - id of the player
  * @returns {Promise} - all player information
  */
  async addJobs (playerId) {
    // Basic job parameters
    const baseJobParams = {
      player_id: playerId,
      state: 'WAITING'
    }

    // Basic parameters for all cars related jobs
    const baseCarJobParam = Object.assign({
      worker_type: 'CAR'
    }, baseJobParams)

    // Drive Job
    const driveJob = Object.assign({
      name: 'DRIVE',
      parameters: JSON.stringify({ drive_time: 10 }, null, 2), // 30 sec of driving session
      worker_id: null
    }, baseCarJobParam)

    // Recording Job
    const recordJob = Object.assign({
      name: 'RECORD',
      parameters: JSON.stringify({ drive_time: 20 }, null, 2) // 60 sec of recording
      // We don't set the worker_id as it will be set by the drive job before this job to used the same car
    }, baseCarJobParam)

    // TODO: add the driving with model job here assume the model name will be "remplaced" or passed automatically if not given

    // Pipeline : Drive -> Record
    const chainedJobs = Object.assign({
      next_job_details: JSON.stringify(recordJob, null, 2)
    }, driveJob)
    console.log('chainedJobs: %o', chainedJobs)
    const response = await axios.post(this.apiUrl + '/jobs', chainedJobs)
    return response.data
  }

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @param {int} player - id of the player
  * @returns {Promise} - all player information
  */
  async removeJob (job) {
    const response = await axios.post(this.apiUrl + '/jobs/' + String(job.job_id) + '/cancel')
    return response.data
  }

  async pauseJobs (player) {
    const response = await axios.post(this.apiUrl + '/jobs/' + String(player.job_id) + '/pause')
    return response.data
  }

  async resumeJob (job) {
    const response = await axios.post(this.apiUrl + '/jobs/' + String(job.job_id) + '/resume')
    return response.data
  }

  async getJobCar (carId) {
    const response = await axios.get(this.apiUrl + '/jobs/?by_rank=true&skip=0&limit=100&worker_id=' + String(carId) + '&job_states=RUNNING&job_states=PAUSING&job_states=PAUSED&job_states=RESUMING&job_states=CANCELLING&job_states=PAUSED')
    return response.data
  }

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @returns {Promise} - all player information
  */
  async getRunningJobs () {
    const response = await axios.get(this.apiUrl + '/jobs/?by_rank=true&skip=0&limit=100&job_states=RUNNING&job_states=PAUSING&job_states=PAUSED&job_states=RESUMING&job_states=CANCELLING')
    return response.data
  }
}
