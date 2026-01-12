const common = {
    state: {
        defaultTableHeight: 800,
        userRole: '',
        fullPath: '',
        hasMsg: false,
        showHistory: false,
        showSchedule: false
    },
    mutations: {
        setDefaultTableHeight: (state, val) => {
            state.defaultTableHeight = val
        },
        setUserRole: (state, val) => {
            state.userRole = val
        },
        setFullPath: (state, val) => {
            state.fullPath = val
        },
        setHasMsg: (state, val) => {
            state.hasMsg = val
        },
        setShowHistory: (state, val) => {
            state.showHistory = val
        },
        setShowSchedule: (state, val) => {
            state.showSchedule = val
        }
    }
}

export default common
