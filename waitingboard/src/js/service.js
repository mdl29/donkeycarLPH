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
  * @returns {Promise<undefined>} -
  */
  async addPlayerToDatabase (pseudo) {
    const response = await axios.post(this.apiUrl + '/players', {
      player_pseudo: pseudo
    })
    return response
  }

  /**
  *
  * @async
  * @augments ScratchyService
  * @param {int} skip - first player , e.g: 0
  * @param {int} limit - last player, e.g: 20
  * @returns {Promise<AllRoom>} - all player information
  */
  async getAllplayers (skip, limit) {
    const response = await axios.get(this.apiUrl + '/players')
    return response.data
  }

  /**
  *
  * @async
  * @augments ScratchyService
  * @param {Boolean} rank - sorted by rank or not
  * @param {int} skip - first player , e.g: 0
  * @param {int} limit - last player, e.g: 20
  * @returns {Promise<AllRoom>} - all player information
  */
  async getDrivingWaitingQueue (rank, skip, limit) {
    const response = await axios.get('http://localhost:8000/drivingWaitingQueue/?by_rank=&skip=0&limit=20')
    return response.data
  }
}
