const getters = {
    getUserRole: state => state.common.userRole,
    geFullPath: state => state.common.fullPath,
    getHasMsg: state => state.common.hasMsg,
    getShowHistory: state => state.common.showHistory,
    getShowSchedule: state => state.common.showSchedule
}
export default getters
