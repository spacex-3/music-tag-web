<template>
    <div class="monitor-navigation-header">
        <div class="header-title">
            <span class="header-title-icon" @click="handleBack" v-if="$route.meta.hasOwnProperty('back')">
                <svg class="icon"
                    style="width: 1em; height: 1em;vertical-align: middle;fill: currentColor;overflow: hidden;"
                    viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4756">
                    <path d="M416 480h320v64H416l96 96-48 48-176-176 176-176 48 48-96 96z" p-id="4757"></path>
                </svg>
            </span>
        </div>
        <div style="display: flex;justify-content: center;align-items: center;">
            <span v-if="scheduleCountdown" style="color: #63656E; font-size: 12px; margin-right: 15px;">
                下次运行: {{ scheduleCountdown }}
            </span>
            <bk-button :text="true" title="配置网易 Cookies" @click="openCookieConfig" style="color: #63656E; margin-right: 20px;">
                <bk-icon type="cog"></bk-icon> 配置 Cookies
            </bk-button>
            <bk-button :text="true" title="定时刮削" @click="openSchedule" style="color: #63656E; margin-right: 20px;">
                <bk-icon type="clock"></bk-icon> 定时刮削
            </bk-button>
            <bk-button :text="true" title="刮削记录" @click="openHistory" style="color: #63656E;">
                <bk-icon type="list"></bk-icon> 历史记录
            </bk-button>
        </div>



        <!-- Netease Cookie Config Dialog -->
        <bk-dialog v-model="cookieVisible"
            theme="primary"
            :mask-close="false"
            title="更新网易云 Cookies"
            @confirm="handleUpdateCookies">
            <p style="margin-bottom: 10px;">粘贴完整的 Cookie 字符串 (key=value; key2=value2) 或 JSON 格式。</p>
            <bk-input type="textarea" :rows="5" v-model="cookieStr" placeholder="MUSIC_U=...; __csrf=..."></bk-input>
        </bk-dialog>
    </div>
</template>

<script>
    import {clearStore} from '../../../common/store.js'
    import {mapGetters} from 'vuex'

    export default {
        data() {
            return {
                logout_url: 'https://github.com/xhongc/music-tag-web',
                pageTitle: '测试',
                userData: {},
                scheduleCountdown: '',
                timer: null,
                pollTimer: null,
                scheduleConfig: {},
                msgList: [],
                cookieVisible: false,
                cookieStr: '',
                user: {
                    list: [
                        '关于作者'
                    ]
                }
            }
        },
        computed: {
            ...mapGetters(['getHasMsg']),
            refresh() {
                if (this.getHasMsg) {
                    this.$store.commit('setHasMsg', false)
                    this.fetchRecord()
                }
            },
            headerTitle() {
                return this.$route.meta.title
            }
        },
        created() {
            this.loginUser()
            this.fetchRecord()
            this.initSchedulePolling()
        },

        watch: {
            getShowSchedule(val) {
                // When dialog closes (val becomes false), refresh the schedule
                // because user might have updated the settings.
                if (!val) {
                    this.fetchSchedule()
                }
            }
        },
        destroyed() {
            if (this.timer) clearInterval(this.timer)
            if (this.pollTimer) clearInterval(this.pollTimer)
        },
        methods: {
            updateCountdown() {
                const config = this.scheduleConfig
                
                // Use last_run_at if available, otherwise use date_changed (creation/update time)
                const anchorTime = config.last_run_at || config.date_changed
                if (!anchorTime) {
                     this.scheduleCountdown = '准备中...' 
                     return
                }

                const lastRun = new Date(anchorTime).getTime()
                let intervalMs = 0
                if (config.interval_unit === 'minutes') {
                    intervalMs = config.interval_hours * 60 * 1000
                } else {
                    // Default to hours
                    intervalMs = config.interval_hours * 60 * 60 * 1000
                }
                let nextRun = lastRun + intervalMs
                const now = new Date().getTime()
                
                let diff = nextRun - now
                
                // If diff is negative (overdue), calculate the NEXT future run time 
                // by adding intervals until it's future.
                if (diff <= 0) {
                   const missedIntervals = Math.ceil(Math.abs(diff) / intervalMs)
                   // If diff is exactly 0 or multiple, add 1 more to be safe? 
                   // Usually Math.ceil on abs helps. 
                   // Example: diff = -100, interval = 1000. abs/int = 0.1 -> ceil = 1. next = last + 1*1000.
                   // diff = -1100. abs/int = 1.1 -> ceil = 2. next = last + 2*1000.
                   // However, missedIntervals might start from 0 if just slightly past.
                   // We want nextRun to be > now.
                   
                   // Simplest: just add intervalMs until > now (avoid loop for large diffs using math)
                   // nextRun_future = lastRun + (floor((now - lastRun) / interval) + 1) * interval
                   const intervalsPassed = Math.floor((now - lastRun) / intervalMs) + 1
                   nextRun = lastRun + (intervalsPassed * intervalMs)
                   diff = nextRun - now
                }

                const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
                const seconds = Math.floor((diff % (1000 * 60)) / 1000)
                
                this.scheduleCountdown = `${hours}h ${minutes}m ${seconds}s`
            },
            startTicker() {
                if (this.timer) clearInterval(this.timer)
                this.updateCountdown()
                this.timer = setInterval(this.updateCountdown, 1000)
            },
            fetchSchedule() {
                this.$api.Task.getScheduleConfig().then((res) => {
                    if (res.result) {
                        this.scheduleConfig = res.data
                        // Even if disabled, we update config so the watcher/timer sees it.
                        this.updateCountdown() 
                    }
                })
            },
            initSchedulePolling() {
                 this.fetchSchedule()
                 this.startTicker()
                 // Poll server every 30s to check for 'last_run_at' updates
                 if (this.pollTimer) clearInterval(this.pollTimer)
                 this.pollTimer = setInterval(this.fetchSchedule, 30000)
            },
            changeTitle() {
            },
            openCookieConfig() {
                this.cookieVisible = true
            },
            handleUpdateCookies() {
                if (!this.cookieStr) {
                    this.$cwMessage('Cookies 不能为空', 'error')
                    return
                }
                this.$api.Task.updateCookies({ cookies: this.cookieStr }).then((res) => {
                    if (res.result) {
                        this.$cwMessage('Cookies 更新成功', 'success')
                        this.cookieStr = '' 
                        this.cookieVisible = false
                    } else {
                        this.$cwMessage('Cookies 更新失败: ' + res.message, 'error')
                    }
                })
            },
            handleRedirect(item) {
                console.log(item.parent_path)
                this.$store.commit('setFullPath', item.parent_path)
            },
            handleUserListClick(e) {
                const btn = document.createElement('a')
                btn.setAttribute('href', this.logout_url)
                document.body.appendChild(btn)
                btn.click()
                clearStore()
            },
            handleUserListClic2k(e) {
                const btn = document.createElement('a')
                btn.setAttribute('href', '/admin/')
                document.body.appendChild(btn)
                btn.click()
                clearStore()
            },
            handleUserListClic3k(e) {
                const btn = document.createElement('a')
                btn.setAttribute('href', 'https://xiers-organization.gitbook.io/music-tag-web/')
                document.body.appendChild(btn)
                btn.click()
                clearStore()
            },
            loginUser() {
                this.$api.Task.loginInfo().then((res) => {
                    if (res.result) {
                        this.userData = res.data
                        this.$store.commit('setUserRole', res.data.role)
                    } else {
                        this.$router.push({name: 'login'})
                    }
                })
            },
            handleBack() {
                this.$router.go(-1)
            },
            fetchRecord() {
                this.$api.Task.getRecord({'state': 'failed', 'page_size': 20}).then((res) => {
                    if (res.result) {
                        this.msgList = res.data.items
                    }
                })
            },
            openHistory() {
                this.$store.commit('setShowHistory', true)
            },
            openSchedule() {
                this.$store.commit('setShowSchedule', true)
            },
        }
    }
</script>

<style scoped>
.monitor-navigation-header {
    -webkit-box-flex: 1;
    -ms-flex: 1;
    flex: 1;
    height: 100%;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
}

.monitor-navigation-header .header-title {
    color: #63656E;
    font-size: 16px;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    margin-left: -6px;
}

.monitor-navigation-header .header-title-icon {
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    width: 28px;
    height: 28px;
    font-size: 28px;
    color: #3A84FF;
    cursor: pointer;
}

.monitor-navigation-header .header-select {
    width: 240px;
    margin-left: auto;
    margin-right: 34px;
    border: none;
    background: #f0f1f5;
    color: #63656e;
    -webkit-box-shadow: none;
    box-shadow: none
}

.monitor-navigation-header .header-user {
    height: 100%;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    -webkit-box-pack: center;
    -ms-flex-pack: center;
    justify-content: center;
    color: #96A2B9;
    /*       margin-left: 8px; */
}

.monitor-navigation-header .header-user .bk-icon {
    margin-left: 5px;
    font-size: 12px;
}

.monitor-navigation-header .header-user:hover {
    cursor: pointer;
    color: #3A84FF
}

.monitor-navigation-admin {
    width: 170px #63656E;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
    -ms-flex-direction: column;
    flex-direction: column;
    background: #FFFFFF;
    border: 1px solid #E2E2E2;
    -webkit-box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
    box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
    padding: 6px 0;
    margin: 0;
    color: #63656E;
}

.monitor-navigation-admin .nav-item {
    -webkit-box-flex: 0;
    -ms-flex: 0 0 32px;
    flex: 0 0 32px;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    padding: 0 20px;
    list-style: none
}

.monitor-navigation-admin .nav-item:hover {
    color: #3A84FF;
    cursor: pointer;
    background-color: #F0F1F5;
}

.navigation-header {
    display: flex;
    justify-content: space-between;
    width: 100%;
    align-items: center;
    font-size: 14px;
}

.monitor-navigation-header .header-mind {
    color: #768197;
    font-size: 16px;
    position: relative;
    height: 32px;
    width: 32px;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    -webkit-box-pack: center;
    -ms-flex-pack: center;
    justify-content: center;
    margin-right: 8px
}

.monitor-navigation-header .header-mind.is-left {
    color: #63656E;
}

.monitor-navigation-header .header-mind.is-left:hover {
    color: #3A84FF;
    background: #F0F1F5
}

.monitor-navigation-header .header-mind-mark {
    position: absolute;
    right: 8px;
    top: 8px;
    height: 7px;
    width: 7px;
    border: 1px solid #27334C;
    background-color: #EA3636;
    border-radius: 100%
}

.monitor-navigation-header .header-mind-mark.is-left {
    border-color: #F0F1F5;
}

.monitor-navigation-header .header-mind:hover {
    background: -webkit-gradient(linear, right top, left top, from(rgba(37, 48, 71, 1)), to(rgba(38, 50, 71, 1)));
    background: linear-gradient(270deg, rgba(37, 48, 71, 1) 0%, rgba(38, 50, 71, 1) 100%);
    border-radius: 100%;
    cursor: pointer;
    color: #D3D9E4;
}

.monitor-navigation-header .header-mind .lang-icon {
    font-size: 20px;
}

.monitor-navigation-header .header-mind-mark {
    position: absolute;
    right: 8px;
    top: 8px;
    height: 7px;
    width: 7px;
    border: 1px solid #27334C;
    background-color: #EA3636;
    border-radius: 100%
}

.monitor-navigation-header .header-mind-mark.is-left {
    border-color: #F0F1F5;
}

.monitor-navigation-message {
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
    -ms-flex-direction: column;
    flex-direction: column;
    width: 360px;
    background-color: #FFFFFF;
    border: 1px solid #E2E2E2;
    border-radius: 2px;
    -webkit-box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
    box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
    color: #979BA5;
    font-size: 12px;
}

.monitor-navigation-message .message-title {
    -webkit-box-flex: 0;
    -ms-flex: 0 0 48px;
    flex: 0 0 48px;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    color: #313238;
    font-size: 14px;
    padding: 0 20px;
    margin: 0;
    border-bottom: 1px solid #F0F1F5;
}

.monitor-navigation-message .message-list {
    -webkit-box-flex: 1;
    -ms-flex: 1;
    flex: 1;
    max-height: 450px;
    overflow: auto;
    margin: 0;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
    -ms-flex-direction: column;
    flex-direction: column;
    padding: 0;
}

.monitor-navigation-message .message-list-item {
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    width: 100%;
    padding: 0 20px;
}

.monitor-navigation-message .message-list-item .item-message {
    padding: 13px 0;
    line-height: 16px;
    min-height: 42px;
    -webkit-box-flex: 1;
    -ms-flex: 1;
    flex: 1;
    -ms-flex-wrap: wrap;
    flex-wrap: wrap;
    color: #63656E;
}

.monitor-navigation-message .message-list-item .item-date {
    padding: 13px 0;
    margin-left: 16px;
    color: #979BA5;
}

.monitor-navigation-message .message-list-item:hover {
    cursor: pointer;
    background: #F0F1F5;
}

.monitor-navigation-message .message-footer {
    -webkit-box-flex: 0;
    -ms-flex: 0 0 42px;
    flex: 0 0 42px;
    border-top: 1px solid #F0F1F5;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    -webkit-box-pack: center;
    -ms-flex-pack: center;
    justify-content: center;
    color: #3A84FF;
}
</style>

<style>
.tippy-popper .tippy-tooltip.navigation-message-theme {
    padding: 0;
    border-radius: 0;
    -webkit-box-shadow: none;
    box-shadow: none;
}
</style>
