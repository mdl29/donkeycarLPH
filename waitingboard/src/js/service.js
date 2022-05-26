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
  * @param {int} skip - first player , e.g: 0
  * @param {int} limit - last player, e.g: 20
  * @returns {Promise} - all player information
  */
  async getAllplayers (skip, limit) {
    const response = await axios.get(this.apiUrl + '/players')
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
    const response = await axios.get(this.apiUrl + '/drivingWaitingQueue/?by_rank=true&skip=0&limit=100')
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
      'player_pseudo': pseudo
    })
    return response.data
  }

  /**
  *
  * @async
  * @augments donkeycarManagerService
  * @param {int} playerId - id of the player
  * @returns {Promise} - all player information
  */
  async addDrivingWaitingQueue (playerId) {
    const response = await axios.post(this.apiUrl + '/drivingWaitingQueue', {
      'player_id': playerId
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
    const response = await axios.post(this.apiUrl + '/drivingWaitingQueue/' + String(playerId) + '/move_after', {
      'after_player_id': afterId
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
    const response = await axios.post(this.apiUrl + '/drivingWaitingQueue/' + String(playerId) + '/move_before', {
      'before_player_id': beforeId
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
    console.log('new Pseudo :' + Newpseudo)
    console.log(player)
    const response = await axios.put(this.apiUrl + '/players/' + String(player.player_id), {
      player_pseudo: Newpseudo,
      register_datetime: player.register_datetime,
      player_id: player.player_id
    })
    return response.data
  }
}
