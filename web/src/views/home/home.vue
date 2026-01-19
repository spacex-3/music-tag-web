<template>
    <div style="display: flex;flex-wrap: wrap;">
        <div class="file-section">
            <div style="width: 95%;margin-top: 20px;margin-left: 10px;">
                <div style="display: flex;align-items: center;">
                    <bk-icon type="arrows-left-shape" @click="backDir" style="cursor: pointer;"></bk-icon>
                    <bk-input :clearable="true" v-model="filePath"
                        @enter="handleSearchFile"
                        :placeholder="'请输入文件夹路径：'"
                        behavior="simplicity">
                    </bk-input>
                    <bk-icon type="arrows-down-shape" @click="handleSearchFile" style="cursor: pointer;"></bk-icon>
                </div>
                <div style="margin-top: 10px;display: flex;align-items: center;">
                    <bk-input type="text" v-model="searchWord" placeholder="根据文件名称搜索" @enter="handleSearch"></bk-input>
                    <div style="margin-left: 10px;margin-right: 5px;">
                        <bk-dropdown-menu :align="'right'">
                            <template slot="dropdown-trigger">
                                <span class="dropdown-trigger-btn bk-icon icon-sort"
                                    style="cursor: pointer;font-size: 20px;"></span>
                            </template>
                            <ul class="bk-dropdown-list" slot="dropdown-content">
                                <li><a href="javascript:;" @click="changeSorted('name')"
                                    :class="{ 'isSelected': sortedField.includes('name') }">名称</a></li>
                                <li><a href="javascript:;" @click="changeSorted('update_time')"
                                    :class="{ 'isSelected': sortedField.includes('update_time') }">修改时间</a></li>
                                <li><a href="javascript:;" @click="changeSorted('size')"
                                    :class="{ 'isSelected': sortedField.includes('size') }">大小</a></li>
                            </ul>
                        </bk-dropdown-menu>
                    </div>
                    <div style="margin-left: 5px;" title="刷新列表">
                        <bk-button :theme="'default'" @click="handleSearchFile" :icon="'refresh'"></bk-button>
                    </div>
                </div>
                <transition name="bk-slide-fade-down">
                    <div style="margin-top: 10px;" v-show="fadeShowDir">
                        <bk-tree
                            ref="tree1"
                            :data="treeListOne"
                            :multiple="true"
                            :node-key="'id'"
                            :has-border="true"
                            :tpl="tpl"
                            :draggable="true"
                            :drag-sort="true"
                            @on-click="nodeClickOne"
                            @on-check="nodeCheckTwo"
                            @on-expanded="nodeExpandedOne">
                        </bk-tree>
                    </div>
                </transition>
            </div>
        </div>
        <div class="edit-section">
            <div v-if="isScraping" style="padding: 20px; width: 100%; text-align: center; color: #3c96ff; font-weight: bold; font-size: 16px; background-color: #f0f8ff;">
                <bk-icon type="refresh" style="display: inline-block; animation: spin 2s linear infinite; margin-right: 8px;"></bk-icon>
                {{ progressText }}
            </div>
            <transition name="bk-slide-fade-left">
                <div style="margin-left: 40px;width: 500px;height: 100%;overflow-y: auto;overscroll-behavior: none;padding-top: 20px;box-sizing: border-box; background-color: #fff;"
                    v-show="musicInfo.title && checkedIds.length === 0">
                    <div style="width: 100%;display: flex;align-items: center;">
                        <bk-button :theme="'success'" :loading="isLoading" @click="handleClick" class="mr10"
                            style="width: 87%;">
                            保存信息
                        </bk-button>
                        <div style="margin-left: 6px;cursor: pointer;" @click="exampleSetting3.primary.visible = true">
                            <bk-icon type="cog-shape"></bk-icon>
                        </div>

                    </div>

                    <div style="display: flex;margin-bottom: 10px;align-items: center;margin-top: 10px;">
                        <div class="label1 can-copy" v-bk-tooltips="'变量名:${title}'" v-bk-copy="'${title}'">标题：</div>
                        <div style="width: 70%; display: flex;">
                            <bk-input :clearable="true" v-model="musicInfo.title" style="flex: 1;"></bk-input>
                            <bk-button :theme="'primary'" :text="true" size="small" style="margin-left: 5px;" @click="toggleLock('title')">
                                <bk-icon type="search" />
                            </bk-button>
                        </div>
                    </div>
                    <div v-for="(item, index) in showFields" :key="'l1' + index">
                        <div class="edit-item" v-if="item === 'filename'">
                            <div class="label1 can-copy" v-bk-tooltips="'变量名:${filename}'" v-bk-copy="'${filename}'">
                                文件名：
                            </div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.filename"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item can-copy" v-else-if="item === 'artist'">
                            <div class="label1" v-bk-tooltips="'变量名:${artist}'" v-bk-copy="'${artist}'">艺术家：</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.artist"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item can-copy" v-else-if="item === 'album'">
                            <div class="label1" v-bk-tooltips="'变量名:${album}'" v-bk-copy="'${album}'">专辑：</div>
                            <div style="width: 70%; display: flex;">
                                <bk-input :clearable="true" v-model="musicInfo.album" style="flex: 1;"></bk-input>
                                <bk-button :theme="'primary'" :text="true" size="small" style="margin-left: 5px;" @click="openAlbumSearch">
                                    <bk-icon type="search" />
                                </bk-button>
                            </div>
                        </div>
                        <div class="edit-item can-copy" v-else-if="item === 'albumartist'">
                            <div class="label1" v-bk-tooltips="'变量名:${albumartist}'" v-bk-copy="'${albumartist}'">
                                专辑艺术家：
                            </div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.albumartist"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'genre'">
                            <div class="label1">风格：</div>
                            <div style="width: 70%;">
                                <bk-select
                                    :disabled="false"
                                    v-model="musicInfo.genre"
                                    style="width: 100%;background: #fff;"
                                    ext-cls="select-custom"
                                    ext-popover-cls="select-popover-custom"
                                    :placeholder="'请选择歌曲风格'"
                                    searchable>
                                    <bk-option v-for="option in genreList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'language'">
                            <div class="label1">语言：</div>
                            <div style="width: 70%;">
                                <bk-select
                                    :disabled="false"
                                    v-model="musicInfo.language"
                                    style="width: 100%;background: #fff;"
                                    ext-cls="select-custom"
                                    ext-popover-cls="select-popover-custom"
                                    :placeholder="'请选择歌曲语言'"
                                    searchable>
                                    <bk-option v-for="option in languageList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'year'">
                            <div class="label1">年份：</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.year"></bk-input>
                            </div>
                        </div>
                        <div style="display: flex;margin-bottom: 10px;flex-direction: column;"
                            v-else-if="item === 'lyrics'">
                            <div style="display: flex;">
                                <div class="label1">歌词：</div>
                                <div style="width: 70%;">
                                    <bk-input :clearable="true" v-model="musicInfo.lyrics" type="textarea" :rows="15">
                                    </bk-input>
                                </div>
                            </div>
                            <div style="display: flex;margin-top: 10px;">
                                <div class="label1">保存歌词：</div>
                                <bk-switcher v-model="musicInfo.is_save_lyrics_file"></bk-switcher>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'comment'">
                            <div class="label1">描述：</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.comment" type="textarea"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'album_img'">
                            <div class="label1">专辑封面：</div>
                            <div style="display: flex;flex-direction: column;">
                                <div style="width: 70%;display: flex;flex-direction: column;" v-if="reloadImg">
                                    <div>
                                        <bk-upload
                                            :files="files1"
                                            :theme="'picture'"
                                            :multiple="false"
                                            :with-credentials="true"
                                            :header="uploadHeader"
                                            :handle-res-code="handleRes"
                                            :size="{ maxFileSize: 5, maxImgSize: 5 }"
                                            :url="uploadUrl"
                                            name="upload_file"
                                        ></bk-upload>
                                    </div>
                                    <div style="color: #63656e;font-size: 12px;display: flex;">
                                        <div>({{ musicInfo.artwork_w }}*{{ musicInfo.artwork_h }})</div>
                                        <div>{{ musicInfo.artwork_size }}MB</div>
                                    </div>
                                </div>
                                <div style="display: flex;margin-top: 10px;">
                                    <div class="label1">保存图片：</div>
                                    <bk-switcher v-model="musicInfo.is_save_album_cover"></bk-switcher>
                                </div>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'discnumber'">
                            <div class="label1">光盘编号：</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.discnumber"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'tracknumber'">
                            <div class="label1">音轨号：</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfo.tracknumber"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'duration'">
                            <div class="label1">时长：</div>
                            <div style="width: 70%;color: #63656e;font-size: 14px;">
                                {{ musicInfo.duration }} s
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'bit_rate'">
                            <div class="label1">比特率：</div>
                            <div style="width: 70%;color: #63656e;font-size: 14px;">
                                {{ musicInfo.bit_rate }} kbps
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'size'">
                            <div class="label1">文件大小：</div>
                            <div style="width: 70%;color: #63656e;font-size: 14px;">
                                {{ musicInfo.size }} MB
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'album_type'">
                            <div class="label1">专辑类型：</div>
                            <div style="width: 70%;">
                                <bk-select
                                    :disabled="false"
                                    v-model="musicInfo.album_type"
                                    style="width: 250px;background: #fff;"
                                    ext-cls="select-custom"
                                    ext-popover-cls="select-popover-custom"
                                    :placeholder="'请选择专辑类型'"
                                    searchable>
                                    <bk-option v-for="option in albumTypeList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                    </div>
                </div>
            </transition>
            <transition name="bk-slide-fade-left">
                <div style="margin-left: 40px;width: 500px;margin-top: 20px;" v-show="checkedIds.length > 0">
                    <div style="width: 100%; display: flex;">
                        <bk-button :theme="'success'" :loading="isLoading"
                            @click="exampleSetting1.primary.visible = true" class="mr10"
                            style="flex: 1;">
                            自动刮削
                        </bk-button>
                        <bk-button :theme="'primary'" :loading="isLoading" @click="handleBatch" class="mr10"
                            style="flex: 1;">
                            手动批量调整
                        </bk-button>
                        <bk-button :theme="'success'" :loading="isLoading"
                            @click="exampleSetting2.primary.visible = true" class="mr10"
                            style="flex: 1;">
                            整理文件夹
                        </bk-button>
                    </div>
                    <bk-divider>
                        <div style="color: gray;font-size: 12px;">手动刮削参数</div>
                    </bk-divider>
                    <div style="display: flex;margin-bottom: 10px;align-items: center;margin-top: 10px;">
                        <div class="label1 can-copy" v-bk-tooltips="'变量名:${title}'" v-bk-copy="'${title}'">标题：</div>
                        <div style="width: 70%;">
                            <bk-input :clearable="true" v-model="musicInfoManual.title"
                                :placeholder="'支持变量批量修改'"></bk-input>
                        </div>
                    </div>
                    <div v-for="(item, index) in showFields" :key="'l2' + index">
                        <div class="edit-item" v-if="item === 'filename'">
                            <div class="label1 can-copy" v-bk-tooltips="'变量名:${filename}'" v-bk-copy="'${filename}'">
                                文件名：
                            </div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.filename"
                                    :placeholder="'例如：${title}-${album}'"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'artist'">
                            <div class="label1 can-copy" v-bk-tooltips="'变量名:${artist}'" v-bk-copy="'${artist}'">艺术家：
                            </div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.artist"
                                    :placeholder="'具体哪些变量,鼠标悬浮在标题上查看'"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'album'">
                            <div class="label1 can-copy" v-bk-tooltips="'变量名:${album}'" v-bk-copy="'${album}'">专辑：</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.album"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'albumartist'">
                            <div class="label1 can-copy" v-bk-tooltips="'变量名:${albumartist}'"
                                v-bk-copy="'${albumartist}'">专辑艺术家：
                            </div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.albumartist"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'genre'">
                            <div class="label1">风格：</div>
                            <div style="width: 70%;">
                                <bk-select
                                    :disabled="false"
                                    v-model="musicInfoManual.genre"
                                    style="width: 250px;background: #fff;"
                                    ext-cls="select-custom"
                                    ext-popover-cls="select-popover-custom"
                                    :placeholder="'请选择歌曲风格'"
                                    searchable>
                                    <bk-option v-for="option in genreList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'language'">
                            <div class="label1">语言：</div>
                            <div style="width: 70%;">
                                <bk-select
                                    :disabled="false"
                                    v-model="musicInfoManual.language"
                                    style="width: 250px;background: #fff;"
                                    ext-cls="select-custom"
                                    ext-popover-cls="select-popover-custom"
                                    :placeholder="'请选择歌曲语言'"
                                    searchable>
                                    <bk-option v-for="option in languageList"
                                        :key="option.id"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'year'">
                            <div class="label1">年份：</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.year"></bk-input>
                            </div>
                        </div>
                        <div style="display: flex;margin-bottom: 10px;flex-direction: column;"
                            v-else-if="item === 'lyrics'">
                            <div style="display: flex;">
                                <div class="label1">歌词：</div>
                                <div style="width: 70%;">
                                    <bk-input :clearable="true" v-model="musicInfoManual.lyrics" type="textarea"
                                        :rows="15"
                                    ></bk-input>
                                </div>
                            </div>
                            <div style="display: flex;margin-top: 10px;">
                                <div class="label1">保存歌词：</div>
                                <bk-switcher v-model="musicInfoManual.is_save_lyrics_file"></bk-switcher>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'comment'">
                            <div class="label1">描述：</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.comment"
                                    type="textarea"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'album_img'">
                            <div class="label1">专辑封面：</div>
                            <div style="display: flex;flex-direction: column;">
                                <div style="width: 70%;display: flex;flex-direction: column;" v-if="reloadImg">
                                    <div>
                                        <bk-upload
                                            :files="files1"
                                            :theme="'picture'"
                                            :multiple="false"
                                            :with-credentials="true"
                                            :header="uploadHeader"
                                            :handle-res-code="handleResBatch"
                                            :size="{ maxFileSize: 5, maxImgSize: 5 }"
                                            :url="uploadUrl"
                                            name="upload_file"
                                        ></bk-upload>
                                    </div>
                                </div>
                                <div style="display: flex;margin-top: 10px;">
                                    <div class="label1">保存图片：</div>
                                    <bk-switcher v-model="musicInfoManual.is_save_album_cover"></bk-switcher>
                                </div>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'discnumber'">
                            <div class="label1" v-bk-tooltips="'变量名:${discnumber}'">光盘编号：</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.discnumber"></bk-input>
                            </div>
                        </div>
                        <div class="edit-item" v-else-if="item === 'tracknumber'">
                            <div class="label1" v-bk-tooltips="'变量名:${tracknumber}'">音轨号：</div>
                            <div style="width: 70%;">
                                <bk-input :clearable="true" v-model="musicInfoManual.tracknumber"></bk-input>
                            </div>
                        </div>
                    </div>
                </div>
            </transition>
        </div>
        <div class="resource-section">
            <transition name="bk-slide-fade-left">
                <div
                    style="display: flex;flex-direction: column;margin-top: 20px;flex: 1;margin-right: 20px;margin-left: 20px;"
                    v-show="fadeShowDetail">
                    <div v-if="SongList.length === 0">
                        <!-- Music Player Section -->
                        <div v-if="currentPlayingFile" style="padding: 10px; display: flex; flex-direction: column; height: calc(100vh - 140px); overflow: hidden;">
                            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
                                <img v-if="musicInfo.artwork" :src="musicInfo.artwork" style="width: 60px; height: 60px; object-fit: cover; border-radius: 6px; flex-shrink: 0;" />
                                <div v-else style="width: 60px; height: 60px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                    <bk-icon type="music" style="font-size: 24px; color: #fff;"></bk-icon>
                                </div>
                                <div style="flex: 1; min-width: 0;">
                                    <div style="font-weight: bold; font-size: 15px; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{{ musicInfo.title || fileName }}</div>
                                    <div style="color: #666; font-size: 13px; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{{ musicInfo.artist || '未知艺术家' }} - {{ musicInfo.album || '未知专辑' }}</div>
                                </div>
                            </div>
                            <audio ref="audioPlayer" :src="audioSrc" controls style="width: 100%; margin-bottom: 10px; flex-shrink: 0;"
                                @timeupdate="onAudioTimeUpdate" @loadedmetadata="onAudioLoaded" @error="onAudioError"></audio>

                            <!-- Lyrics Offset Controls -->
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; flex-shrink: 0; font-size: 12px; background: #f0f8ff; padding: 4px 8px; border-radius: 4px;">
                                <div style="display: flex; align-items: center;">
                                    <span style="margin-right: 5px;">偏移:</span>
                                    <bk-button :text="true" size="small" @click="adjustLyricsOffset(-0.05)" title="延迟 -50ms">
                                        <bk-icon type="minus-circle-shape" style="font-size: 14px;" />
                                    </bk-button>
                                    <span style="margin: 0 5px; min-width: 50px; text-align: center;">{{ lyricsOffset > 0 ? '+' : '' }}{{ Math.round(lyricsOffset * 1000) }}ms</span>
                                    <bk-button :text="true" size="small" @click="adjustLyricsOffset(0.05)" title="延迟 +50ms">
                                        <bk-icon type="plus-circle-shape" style="font-size: 14px;" />
                                    </bk-button>
                                </div>
                                <bk-button :theme="'primary'" :text="true" size="small" v-if="lyricsOffset !== 0" @click="applyLyricsOffset">
                                    应用到文本
                                </bk-button>
                            </div>

                            <div v-if="parsedLyrics.length" ref="lyricsContainer" style="flex: 1; overflow-y: auto; background: linear-gradient(to bottom, #f8f9fa, #fff); border-radius: 8px; padding: 12px; border: 1px solid #eee; scroll-behavior: smooth;">
                                <div style="text-align: center; line-height: 2; font-size: 13px;">
                                    <div v-for="(lyric, idx) in parsedLyrics" :key="idx"
                                        :ref="'lyricLine' + idx"
                                        :style="{
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            transition: 'all 0.3s ease',
                                            color: idx === currentLyricIndex ? '#3a84ff' : '#666',
                                            fontWeight: idx === currentLyricIndex ? '600' : '400',
                                            fontSize: idx === currentLyricIndex ? '15px' : '13px',
                                            background: idx === currentLyricIndex ? 'rgba(58, 132, 255, 0.1)' : 'transparent'
                                        }">{{ lyric.text }}</div>
                                </div>
                            </div>
                            <div v-else style="flex: 1; display: flex; align-items: center; justify-content: center; color: #999; font-size: 13px; background: #f8f9fa; border-radius: 8px;">
                                暂无歌词
                            </div>
                        </div>
                        <span v-else style="margin-left: 30%;margin-top: 30%;">暂无歌曲信息</span>
                    </div>
                    <div v-else>
                        <div class="parent">
                            <div class="title2">应用</div>
                            <div class="title2">封面</div>
                            <div class="title2">标题</div>
                            <div class="title2">艺术家</div>
                            <div class="title2">专辑</div>
                            <div class="title2">歌词</div>
                            <div class="title2">年份</div>
                        </div>
                        <div v-for="(item,index) in SongList" :key="index" style="margin-bottom: 10px;" class="parent">
                            <bk-icon type="arrows-left-shape" @click="copyAll(item)"
                                style="margin-right: 5px;cursor: pointer;"></bk-icon>
                            <div v-if="resource === 'smart_tag'">
                                <bk-badge class="mr40" :theme="'warning'" :val="item.score" radius="20%">
                                    <bk-image fit="contain" :src="item.album_img"
                                        style="width: 64px;cursor: pointer;"
                                        @click="handleCopy('album_img',item.album_img)">
                                    </bk-image>
                                </bk-badge>
                            </div>
                            <div v-else>
                                <bk-image fit="contain" :src="item.album_img"
                                    style="width: 64px;cursor: pointer;"
                                    @click="handleCopy('album_img',item.album_img, item.source)">
                                </bk-image>
                            </div>
                            <div @click="handleCopy('title',item.name, item.source)" class="music-item">
                                <span v-if="item.source" :style="{ background: item.source === 'netease' ? '#c20c0c' : '#31c27c', color: 'white', padding: '1px 4px', borderRadius: '3px', fontSize: '10px', marginRight: '4px' }">{{ item.source === 'netease' ? '网易云' : 'QQ音乐' }}</span>
                                {{
                                    item.name
                                }}
                            </div>
                            <div @click="handleCopy('artist',item.artist, item.source)" class="music-item">
                                {{ item.artist }}
                            </div>
                            <div @click="handleCopy('album',item.album, item.source)" class="music-item">
                                {{
                                    item.album
                                }}
                            </div>
                            <div @click="handleCopy('lyric',item)" class="music-item">加载歌词</div>
                            <div @click="handleCopy('year',item.year)" class="music-item">
                                {{
                                    item.year
                                }}
                            </div>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                            <bk-divider></bk-divider>
                        </div>
                    </div>
                </div>
            </transition>
            <transition name="bk-slide-fade-left">
                <div v-show="showTranslation">
                    <div style="display: flex;height: 100%;">
                        <bk-icon type="arrows-left-shape" @click="handleCopy('lyric_tran',translationText)"
                            style="margin-right: 5px;margin-left: 15px;margin-top: 50%;cursor: pointer;"></bk-icon>
                        <div style="width: 100%;height: 100%;">
                            <bk-input :clearable="true" v-model="translationText" type="textarea" :rows="50"
                                style="height: 100%;">
                            </bk-input>
                        </div>
                    </div>
                </div>
            </transition>
            <div v-show="!fadeShowDetail && !showTranslation"
                style="width: 90%;height: 90%; margin: 50px 20px 20px 50px;">
                <bk-image fit="contain" :src="'/static/img/bg.png'"
                    style="width: 100%;height: 98%;"></bk-image>
            </div>
        </div>
        <bk-dialog v-model="exampleSetting1.primary.visible"
            theme="primary"
            :mask-close="false"
            @confirm="handleBatchAuto"
            :header-position="exampleSetting1.primary.headerPosition"
            title="自动批量修改">
            <p>宽松模式: 只根据标题匹配元数据, 可能存在同名或翻唱歌曲。</p>
            <p>严格模式: 根据标题和歌手或标题和专辑匹配元数据, 准确性更高。</p>
            <bk-radio-group v-model="selectAutoMode">
                <bk-radio-button value="simple">
                    宽松模式
                </bk-radio-button>
                <bk-radio-button value="hard">
                    严格模式
                </bk-radio-button>
                <bk-radio-button value="strict_album">
                    严格专辑模式 (按文件夹)
                </bk-radio-button>
            </bk-radio-group>
            <div>音乐源顺序</div>
            <bk-select style="width: 250px;"
                searchable
                multiple
                show-select-all
                v-model="sourceList">
                <bk-option v-for="option in resourceListBatch"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select>
            <div style="margin-top: 10px;">覆盖策略</div>
            <bk-radio-group v-model="overwritePolicy" style="margin-top: 5px;">
                <bk-radio-button value="overwrite_all">
                    完全覆盖 (默认)
                </bk-radio-button>
                <bk-radio-button value="overwrite_missing">
                    仅补充缺失
                </bk-radio-button>
            </bk-radio-group>
            <div style="margin-top: 15px;">
                <bk-checkbox v-model="skipScraped">跳过已刮削文件 (历史记录中存在即跳过)</bk-checkbox>
            </div>

        </bk-dialog>
        <bk-dialog v-model="exampleSetting2.primary.visible"
            theme="primary"
            :mask-close="false"
            @confirm="handleTidy"
            :header-position="exampleSetting2.primary.headerPosition"
            title="整理文件夹">
            <p>整理文件夹，按一级目录，二级目录选定的信息分类。</p>
            <p style="color: #666; font-size: 12px; margin-top: 5px;">注意：整理完成后，未成功刮削的文件及残留文件夹将自动移动到当前目录下的【未整理文件】中。</p>
            <div>整理后的根目录</div>
            <div class="input-demo">
                <bk-input v-model="tidyFormData.root_path">
                </bk-input>
            </div>
            <div>一级目录</div>
            <bk-select style="width: 250px;"
                :clearable="false"
                v-model="tidyFormData.first_dir">
                <bk-option v-for="option in tidyList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select>
            <div>二级目录</div>
            <bk-select style="width: 250px;"
                v-model="tidyFormData.second_dir">
                <bk-option v-for="option in tidyList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select>
        </bk-dialog>
        <bk-dialog v-model="scheduleVisible"
            theme="primary"
            :mask-close="false"
            width="600"
            @confirm="saveScheduleConfig"
            title="定时刮削配置">
            <div style="margin-bottom: 20px;">
                <p style="color: #666; margin-bottom: 10px;">定时任务将自动扫描媒体库新增文件，并执行刮削。</p>
            </div>

            <div style="display: flex; flex-direction: column;">
                <div style="margin-bottom: 15px; display: flex; align-items: center;">
                    <span style="width: 100px; text-align: right; margin-right: 20px;">开启任务</span>
                    <bk-switcher v-model="scheduleConfig.enabled"></bk-switcher>
                </div>

                <div style="margin-bottom: 15px; display: flex; align-items: center;">
                    <span style="width: 100px; text-align: right; margin-right: 20px;">执行间隔</span>
                    <bk-input type="number" :min="1" style="width: 160px; margin-right: 10px;" v-model="scheduleConfig.interval_hours"></bk-input>
                    <bk-select v-model="scheduleConfig.interval_unit" style="width: 80px;" :clearable="false">
                        <bk-option id="hours" name="小时"></bk-option>
                        <bk-option id="minutes" name="分钟"></bk-option>
                    </bk-select>
                </div>

                <div style="margin-bottom: 15px; display: flex; align-items: center;">
                    <span style="width: 100px; text-align: right; margin-right: 20px;">刮削模式</span>
                    <bk-select v-model="scheduleConfig.select_mode" style="width: 250px;">
                        <bk-option v-for="option in selectAutoModeList" :key="option.id" :id="option.id" :name="option.name"></bk-option>
                    </bk-select>
                </div>

                <div style="margin-bottom: 15px; display: flex; align-items: center;">
                    <span style="width: 100px; text-align: right; margin-right: 20px;">覆盖策略</span>
                    <bk-select v-model="scheduleConfig.overwrite_policy" style="width: 250px;">
                        <bk-option v-for="option in overwritePolicyList" :key="option.id" :id="option.id" :name="option.name"></bk-option>
                    </bk-select>
                </div>

                <div style="margin-bottom: 15px; display: flex; align-items: center;">
                    <span style="width: 100px; text-align: right; margin-right: 20px;">数据源</span>
                    <bk-checkbox-group v-model="scheduleConfig.source_list">
                        <bk-checkbox :value="'netease'" style="margin-right: 20px;">网易云音乐</bk-checkbox>
                        <bk-checkbox :value="'qmusic'">QQ音乐</bk-checkbox>
                    </bk-checkbox-group>
                </div>

                <div style="margin-bottom: 15px; margin-left: 120px;">
                    <bk-checkbox v-model="scheduleConfig.skip_scraped">跳过已刮削文件 (历史记录中存在的)</bk-checkbox>
                </div>
            </div>
        </bk-dialog>
        <bk-dialog v-model="exampleSetting3.primary.visible"
            theme="primary"
            :mask-close="false"
            @confirm="handleSettings"
            :header-position="exampleSetting3.primary.headerPosition"
            title="配置">
            <p>选择你的配置，浏览器会保存你的默认值</p>
            <div>标签来源</div>
            <bk-select
                :disabled="false"
                :clearable="false"
                v-model="resource"
                style="width: 200px;"
                ext-cls="select-custom"
                ext-popover-cls="select-popover-custom">
                <bk-option v-for="option in resourceList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select>
            <div>展示的字段以及顺序</div>
            <bk-select style="width: 350px;margin-top: 10px;"
                searchable
                :clearable="false"
                multiple
                display-tag
                v-model="showFields">
                <bk-option v-for="option in fieldList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select>

        </bk-dialog>

        <!-- Scrape Result Log Dialog -->
        <bk-dialog v-model="logVisible"
            theme="primary"
            :mask-close="false"
            width="800"
            :show-footer="false"
            title="刮削结果">
            <div style="margin-bottom: 10px;">
                <bk-alert type="success" :title="'成功: ' + (summaryData.success_count || 0)"></bk-alert>
                <bk-alert type="error" :title="'失败: ' + (summaryData.fail_count || 0)" style="margin-top: 5px;"></bk-alert>
                <bk-alert v-if="summaryData.cookie_warning" type="warning" title="警告: 网易云音乐由于缺少Cookie导致搜索失败，请配置Cookie!" style="margin-top: 5px;"></bk-alert>
            </div>
            <div v-if="failedItems.length > 0" style="margin-top: 10px; max-height: 200px; overflow-y: auto;">
                <p><strong>失败列表 (点击跳转):</strong></p>
                <div v-for="(item, idx) in failedItems" :key="'fail-' + idx" style="cursor: pointer; color: red;" @click="handleJump(item)">
                    {{ item.name }}
                </div>
            </div>
            <div style="max-height: 500px; overflow-y: auto; background: #f5f5f5; padding: 10px; border-radius: 4px; font-family: monospace; margin-top: 10px;">
                <div v-for="(log, idx) in scrapeLogs" :key="idx" style="margin-bottom: 2px;" :style="{ color: log.type === 'error' ? 'red' : (log.type === 'warning' ? '#ff9c01' : 'black') }">
                    {{ log.msg }}
                </div>
            </div>
            <div style="margin-top: 10px; text-align: right;">
                <bk-button @click="logVisible = false">关闭</bk-button>
            </div>
        </bk-dialog>

        <!-- History Dialog -->
        <bk-dialog v-model="historyVisible"
            theme="primary"
            :mask-close="true"
            width="800"
            :show-footer="false"
            title="刮削记录">
            <div style="margin-bottom: 15px;">
                <bk-button-group>
                    <bk-button :theme="historyFilter === 'all' ? 'primary' : 'default'" @click="historyFilter = 'all'">
                        全部 ({{ successItems.length + failedItems.length + skippedItems.length }})
                    </bk-button>
                    <bk-button :theme="historyFilter === 'success' ? 'primary' : 'default'" @click="historyFilter = 'success'">
                        成功 ({{ successItems.length }})
                    </bk-button>
                    <bk-button :theme="historyFilter === 'failed' ? 'primary' : 'default'" @click="historyFilter = 'failed'">
                        失败 ({{ failedItems.length }})
                    </bk-button>
                    <bk-button :theme="historyFilter === 'skipped' ? 'primary' : 'default'" @click="historyFilter = 'skipped'">
                        跳过 ({{ skippedItems.length }})
                    </bk-button>
                </bk-button-group>
            </div>
            <div v-if="filteredHistoryItems.length > 0" style="max-height: 400px; overflow-y: auto;">
                <div v-for="(item, idx) in filteredHistoryItems" :key="'hist-' + idx"
                    :style="{ cursor: 'pointer', padding: '8px 12px', borderBottom: '1px solid #eee', color: item.type === 'failed' ? '#ea3636' : (item.type === 'skipped' ? '#ff9c01' : '#2dcb56') }"
                    @click="handleJump(item)">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="margin-right: 8px;">
                                <bk-icon v-if="item.type === 'success'" type="check-circle-shape"></bk-icon>
                                <bk-icon v-else-if="item.type === 'failed'" type="close-circle-shape"></bk-icon>
                                <bk-icon v-else type="exclamation-circle-shape"></bk-icon>
                            </span>
                            {{ item.name }}
                        </div>
                        <div style="font-size: 12px; color: #999; min-width: 140px; text-align: right;">
                            {{ item.display_time }}
                        </div>
                    </div>
                    <div v-if="item.detail_msg && item.type === 'success'" style="color: #2dcb56; font-size: 12px; margin-left: 24px; margin-top: 4px;">
                        {{ item.detail_msg }}
                    </div>
                    <div v-if="item.error_msg && item.type === 'failed'" style="color: #ea3636; font-size: 12px; margin-left: 24px; margin-top: 4px;">
                        {{ item.error_msg }}
                    </div>
                </div>
            </div>
            <div v-else style="text-align: center; padding: 40px; color: #999;">
                暂无记录
            </div>
            <div style="margin-top: 15px; text-align: right;">
                <bk-button @click="historyVisible = false">关闭</bk-button>
            </div>
        </bk-dialog>

        <!-- Statistics Dialog -->
        <bk-dialog v-model="statsVisible"
            theme="primary"
            :mask-close="true"
            width="1000"
            :show-footer="false"
            title="媒体统计">
            <div v-if="statsLoading" style="text-align: center; padding: 40px;">
                <bk-icon type="refresh" style="animation: spin 2s linear infinite; font-size: 24px;"></bk-icon>
                <div style="margin-top: 10px;">正在扫描媒体库...</div>
            </div>
            <div v-else-if="statsData || statsDetailData">
                <!-- Breadcrumb Navigation -->
                <div style="margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                    <span @click="resetStatsView" style="cursor: pointer; color: #3a84ff;">首页</span>
                    <span v-if="statsBreadcrumb.length > 0" style="color: #999;">→</span>
                    <span v-for="(crumb, idx) in statsBreadcrumb" :key="idx" style="display: flex; align-items: center; gap: 8px;">
                        <span @click="navigateBreadcrumb(idx)" :style="{ cursor: idx < statsBreadcrumb.length - 1 ? 'pointer' : 'default', color: idx < statsBreadcrumb.length - 1 ? '#3a84ff' : '#333' }">
                            {{ crumb.label }}
                        </span>
                        <span v-if="idx < statsBreadcrumb.length - 1" style="color: #999;">→</span>
                    </span>
                </div>

                <!-- Level 0: Main Stats View -->
                <div v-if="statsDetailData === null && statsData">
                    <div style="margin-bottom: 15px; color: #666;">
                        共扫描 <strong>{{ statsData.total_files }}</strong> 个文件
                    </div>
                    <bk-button-group style="margin-bottom: 15px;">
                        <bk-button :theme="statsTab === 'albums' ? 'primary' : 'default'" @click="statsTab = 'albums'">
                            📀 专辑 ({{ statsData.albums_count }})
                        </bk-button>
                        <bk-button :theme="statsTab === 'artists' ? 'primary' : 'default'" @click="statsTab = 'artists'">
                            🎤 艺术家 ({{ statsData.artists_count }})
                        </bk-button>
                        <bk-button :theme="statsTab === 'album_artists' ? 'primary' : 'default'" @click="statsTab = 'album_artists'">
                            👥 专辑艺术家 ({{ statsData.album_artists_count }})
                        </bk-button>
                        <bk-button :theme="statsTab === 'has_info' ? 'primary' : 'default'" @click="statsTab = 'has_info'">
                            ✅ 有信息 ({{ statsData.has_info_count }})
                        </bk-button>
                        <bk-button :theme="statsTab === 'no_info' ? 'primary' : 'default'" @click="statsTab = 'no_info'">
                            ❌ 无信息 ({{ statsData.no_info_count }})
                        </bk-button>
                    </bk-button-group>

                    <div style="max-height: 400px; overflow-y: auto;">
                        <!-- Albums Tab - Direct to songs -->
                        <div v-if="statsTab === 'albums'">
                            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                                <thead>
                                    <tr style="background: #f5f5f5; text-align: left;">
                                        <th style="padding: 10px; border-bottom: 2px solid #ddd;">专辑</th>
                                        <th style="padding: 10px; border-bottom: 2px solid #ddd;">专辑艺术家</th>
                                        <th style="padding: 10px; border-bottom: 2px solid #ddd; width: 80px;">歌曲数</th>
                                        <th style="padding: 10px; border-bottom: 2px solid #ddd; width: 100px;">刮削信息</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="(item, idx) in statsData.albums" :key="'album-' + idx"
                                        style="cursor: pointer;" :style="{ background: idx % 2 === 0 ? '#fff' : '#fafafa' }"
                                        @click="drillDownAlbum(item.name)">
                                        <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: 500;">{{ item.name }}</td>
                                        <td style="padding: 10px; border-bottom: 1px solid #eee; color: #666;">{{ item.albumartist || '-' }}</td>
                                        <td style="padding: 10px; border-bottom: 1px solid #eee;">{{ item.count }}</td>
                                        <td style="padding: 10px; border-bottom: 1px solid #eee;">
                                            <span :style="{ color: item.scraped_count === item.count ? '#2dcb56' : '#ff9c01' }">
                                                {{ item.scraped_count }}/{{ item.count }}
                                            </span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- Artists Tab - Drill to albums -->
                        <div v-if="statsTab === 'artists'">
                            <div v-for="(item, idx) in statsData.artists" :key="'artist-' + idx"
                                style="padding: 10px 12px; border-bottom: 1px solid #eee; cursor: pointer; display: flex; justify-content: space-between; align-items: center;"
                                @click="drillDownArtist(item.name)" :style="{ background: idx % 2 === 0 ? '#fff' : '#fafafa' }">
                                <span style="font-weight: 500;">{{ item.name }}</span>
                                <span style="color: #999; font-size: 13px;">{{ item.count }} 首</span>
                            </div>
                        </div>

                        <!-- Album Artists Tab - Drill to albums -->
                        <div v-if="statsTab === 'album_artists'">
                            <div v-for="(item, idx) in statsData.album_artists" :key="'aa-' + idx"
                                style="padding: 10px 12px; border-bottom: 1px solid #eee; cursor: pointer; display: flex; justify-content: space-between; align-items: center;"
                                @click="drillDownAlbumArtist(item.name)" :style="{ background: idx % 2 === 0 ? '#fff' : '#fafafa' }">
                                <span style="font-weight: 500;">{{ item.name }}</span>
                                <span style="color: #999; font-size: 13px;">{{ item.count }} 首</span>
                            </div>
                        </div>

                        <!-- Has Info Tab -->
                        <div v-if="statsTab === 'has_info'">
                            <div v-for="(item, idx) in statsData.has_info" :key="'hi-' + idx"
                                style="padding: 8px 12px; border-bottom: 1px solid #eee; cursor: pointer;"
                                @click="navigateToStatsItem(item)">
                                <div>{{ item.filename }}</div>
                                <div style="font-size: 12px; color: #666;">
                                    {{ item.artist }} - {{ item.album }}
                                    <span v-if="item.has_lyrics" style="color: #2dcb56; margin-left: 8px;">有歌词</span>
                                    <span v-if="item.has_cover" style="color: #2dcb56; margin-left: 8px;">有封面</span>
                                </div>
                            </div>
                        </div>

                        <!-- No Info Tab -->
                        <div v-if="statsTab === 'no_info'">
                            <div v-for="(item, idx) in statsData.no_info" :key="'ni-' + idx"
                                style="padding: 8px 12px; border-bottom: 1px solid #eee; cursor: pointer; color: #ea3636;"
                                @click="navigateToStatsItem(item)">
                                <div>{{ item.filename }}</div>
                                <div style="font-size: 12px; color: #999;">{{ item.parent_path }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Level 1: Albums List (from Artist/AlbumArtist drill-down) -->
                <div v-if="statsDetailData && statsDetailData.type === 'albums'">
                    <div style="margin-bottom: 15px; color: #666;">
                        {{ statsDetailData.name }} 共有 <strong>{{ statsDetailData.albums.length }}</strong> 张专辑，<strong>{{ statsDetailData.total_songs }}</strong> 首歌
                    </div>
                    <div style="max-height: 400px; overflow-y: auto;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background: #f5f5f5; text-align: left;">
                                    <th style="padding: 10px; border-bottom: 2px solid #ddd;">专辑</th>
                                    <th style="padding: 10px; border-bottom: 2px solid #ddd; width: 80px;">歌曲数</th>
                                    <th style="padding: 10px; border-bottom: 2px solid #ddd; width: 100px;">有刮削信息</th>
                                    <th style="padding: 10px; border-bottom: 2px solid #ddd; width: 80px;">年份</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(album, idx) in statsDetailData.albums" :key="idx"
                                    style="cursor: pointer;" :style="{ background: idx % 2 === 0 ? '#fff' : '#fafafa' }"
                                    @click="drillDownAlbum(album.name)">
                                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{{ album.name }}</td>
                                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{{ album.song_count }}</td>
                                    <td style="padding: 10px; border-bottom: 1px solid #eee;">
                                        <span :style="{ color: album.scraped_count === album.song_count ? '#2dcb56' : '#ff9c01' }">
                                            {{ album.scraped_count }}/{{ album.song_count }}
                                        </span>
                                    </td>
                                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{{ album.year || '-' }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Level 2: Songs List (from Album drill-down) -->
                <div v-if="statsDetailData && statsDetailData.type === 'songs'">
                    <div style="margin-bottom: 15px; color: #666;">
                        专辑《{{ statsDetailData.name }}》共有 <strong>{{ statsDetailData.total_songs }}</strong> 首歌
                    </div>
                    <div style="max-height: 400px; overflow-y: auto;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                            <thead>
                                <tr style="background: #f5f5f5; text-align: left;">
                                    <th style="padding: 8px; border-bottom: 2px solid #ddd;">标题</th>
                                    <th style="padding: 8px; border-bottom: 2px solid #ddd;">艺术家</th>
                                    <th style="padding: 8px; border-bottom: 2px solid #ddd;">专辑艺术家</th>
                                    <th style="padding: 8px; border-bottom: 2px solid #ddd;">年份</th>
                                    <th style="padding: 8px; border-bottom: 2px solid #ddd;">流派</th>
                                    <th style="padding: 8px; border-bottom: 2px solid #ddd; text-align: center;">歌词</th>
                                    <th style="padding: 8px; border-bottom: 2px solid #ddd; text-align: center;">封面</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(song, idx) in statsDetailData.songs" :key="idx"
                                    style="cursor: pointer;" :style="{ background: idx % 2 === 0 ? '#fff' : '#fafafa' }"
                                    @click="navigateToStatsItem(song)">
                                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{{ song.title }}</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{{ song.artist || '-' }}</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{{ song.albumartist || '-' }}</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{{ song.year || '-' }}</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{{ song.genre || '-' }}</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">
                                        <span :style="{ color: song.has_lyrics ? '#2dcb56' : '#ccc' }">{{ song.has_lyrics ? '✓' : '✗' }}</span>
                                    </td>
                                    <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">
                                        <span :style="{ color: song.has_cover ? '#2dcb56' : '#ccc' }">{{ song.has_cover ? '✓' : '✗' }}</span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div v-else style="text-align: center; padding: 40px; color: #999;">
                请先选择一个媒体目录
            </div>
            <div style="margin-top: 15px; text-align: right;">
                <bk-button @click="statsVisible = false">关闭</bk-button>
            </div>
        </bk-dialog>

        <!-- Album Search Dialog -->
        <bk-dialog v-model="albumSearchVisible"
            theme="primary"
            :mask-close="false"
            width="900"
            :show-footer="false"
            title="搜索专辑">
            <div style="display: flex; margin-bottom: 10px;">
                <bk-input v-model="albumSearchQuery" placeholder="输入专辑名称" @enter="searchAlbum" style="flex: 1; margin-right: 10px;"></bk-input>
                <bk-button :theme="'primary'" @click="searchAlbum" :loading="isAlbumSearching">搜索</bk-button>
                <bk-button v-if="selectedAlbum" @click="backToAlbumList" style="margin-left: 10px;">返回专辑列表</bk-button>
            </div>

            <!-- Step 1: Album List -->
            <div v-if="!selectedAlbum && albumList.length > 0" style="max-height: 450px; overflow-y: auto;">
                <div style="margin-bottom: 10px; color: #666;">
                    找到 {{ albumList.length }} 个专辑
                    <span :style="{ background: resource === 'netease' ? '#c20c0c' : '#31c27c', color: 'white', padding: '2px 6px', borderRadius: '3px', fontSize: '12px', marginLeft: '8px' }">
                        {{ resource === 'netease' ? '网易云' : 'QQ音乐' }}
                    </span>
                </div>
                <div v-for="(album, idx) in albumList" :key="'album-' + idx"
                    style="padding: 12px; border: 1px solid #eee; border-radius: 4px; margin-bottom: 8px; cursor: pointer; display: flex; align-items: center; transition: background 0.2s;"
                    @click="selectAlbum(album)"
                    @mouseover="$event.target.style.background = '#f5f7fa'"
                    @mouseout="$event.target.style.background = 'white'">
                    <img :src="album.cover" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px; margin-right: 12px;" />
                    <div style="flex: 1;">
                        <div style="font-weight: bold; font-size: 14px;">{{ album.name }}</div>
                        <div style="color: #666; font-size: 12px; margin-top: 4px;">{{ album.artist }}</div>
                        <div style="color: #999; font-size: 12px;">{{ album.year }} · {{ album.size }} 首</div>
                    </div>
                </div>
            </div>

            <!-- Step 2: Track List -->
            <div v-if="selectedAlbum && albumSearchResults" style="max-height: 450px; overflow-y: auto;">
                <div style="display: flex; align-items: center; margin-bottom: 15px; padding: 10px; background: #f5f7fa; border-radius: 4px;">
                    <img :src="albumSearchResults.album_img" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px; margin-right: 15px;" />
                    <div>
                        <div style="font-weight: bold; font-size: 16px;">
                            {{ albumSearchResults.album_name }}
                            <span :style="{ background: resource === 'netease' ? '#c20c0c' : '#31c27c', color: 'white', padding: '2px 6px', borderRadius: '3px', fontSize: '11px', marginLeft: '8px' }">
                                {{ resource === 'netease' ? '网易云' : 'QQ音乐' }}
                            </span>
                        </div>
                        <div style="color: #666; margin-top: 4px;">{{ albumSearchResults.album_artist }}</div>
                        <div style="color: #999; font-size: 12px;">{{ albumSearchResults.year }} · {{ albumSearchResults.tracks.length }} 首</div>
                    </div>
                    <div style="margin-left: auto;">
                        <bk-button :theme="'success'" size="small" @click="handleAutoMatchScores">一键自动匹配</bk-button>
                    </div>
                </div>
                <div v-for="(track, idx) in albumSearchResults.tracks" :key="'track-' + idx"
                    style="padding: 10px 12px; border-bottom: 1px solid #eee; cursor: pointer; display: flex; align-items: center;"
                    @click="applyAlbumTrack(track)"
                    @mouseover="$event.target.style.background = '#f5f7fa'"
                    @mouseout="$event.target.style.background = 'white'">
                    <div style="width: 30px; color: #999;">{{ track.idx }}</div>
                    <div style="flex: 1;">
                        <div>{{ track.name }}</div>
                        <div style="color: #999; font-size: 12px;">{{ track.artist }}</div>
                    </div>
                    <bk-button :theme="'primary'" :text="true" size="small">应用</bk-button>
                </div>
            </div>

            <div v-if="albumList.length === 0 && !selectedAlbum && !isAlbumSearching" style="text-align: center; color: #999; padding: 40px;">
                输入专辑名称搜索
            </div>

            <div style="margin-top: 15px; text-align: right;">
                <bk-button @click="albumSearchVisible = false">关闭</bk-button>
            </div>
        </bk-dialog>

    </div>
</template>
<script>
    import {mapGetters} from 'vuex'

    export default {
        data() {
            return {
                files1: [],
                uploadUrl: '/api/upload_image/',
                uploadHeader: [
                    {name: 'X-CSRFToken', value: this.getCookie('django_vue_cli_csrftoken')},
                    {name: 'AUTHORIZATION', value: this.getCookie('AUTHORIZATION')}
                ],
                showFields: localStorage.getItem('showFields') ? JSON.parse(localStorage.getItem('showFields')) : ['filename', 'artist', 'album', 'albumartist', 'genre', 'year', 'lyrics', 'comment', 'album_img'],
                fieldList: [
                    {id: 'filename', name: '文件名'},
                    {id: 'artist', name: '艺术家'},
                    {id: 'album', name: '专辑'},
                    {id: 'album_type', name: '专辑类型'},
                    {id: 'albumartist', name: '专辑艺术家'},
                    {id: 'discnumber', name: '光盘编号'},
                    {id: 'tracknumber', name: '音轨号'},
                    {id: 'genre', name: '风格'},
                    {id: 'year', name: '年份'},
                    {id: 'lyrics', name: '歌词'},
                    {id: 'comment', name: '描述'},
                    {id: 'album_img', name: '专辑封面'},
                    {id: 'duration', name: '时长'},
                    {id: 'size', name: '文件大小'},
                    {id: 'bit_rate', name: '比特率'},
                    {id: 'language', name: '语言'}
                ],
                albumTypeList: [
                    {id: 'album;compilation', name: '合集'},
                    {id: 'album;live', name: '现场'},
                    {id: 'album;remix', name: '混音'},
                    {id: 'album;soundtrack', name: '原声'},
                    {id: 'album;demo', name: '演示'},
                    {id: 'album;album', name: '普通'},
                    {id: 'ep', name: 'EP'},
                    {id: 'single', name: '单曲'}
                ],
                searchWord: '',
                treeListOne: [],
                fullPath: '',
                fileName: '',
                resource: localStorage.getItem('resource') ? localStorage.getItem('resource') : 'netease',
                translationText: '',
                resourceList: [
                    {id: 'netease', name: '网易云音乐'},
                    {id: 'qmusic', name: 'QQ音乐'}
                ],
                resourceListBatch: [
                    {id: 'netease', name: '网易云音乐'},
                    {id: 'qmusic', name: 'QQ音乐'}
                ],
                selectAutoModeList: [
                    { id: 'normal', name: '普通模式' },
                    { id: 'strict_album', name: '严格专辑模式' }
                ],
                overwritePolicyList: [
                    { id: 'overwrite_all', name: '完全覆盖' },
                    { id: 'overwrite_missing', name: '仅覆盖缺失' }
                ],
                tidyList: [
                    {id: 'title', name: '标题'},
                    {id: 'artist', name: '艺术家'},
                    {id: 'album', name: '专辑'},
                    {id: 'albumartist', name: '专辑艺术家'},
                    {id: 'album_type', name: '专辑类型'},
                    {id: 'genre', name: '风格'},
                    {id: 'language', name: '语言'},
                    {id: 'comment', name: '描述'}
                ],
                baseMusicInfo: {
                    'genre': '流行',
                    'is_save_lyrics_file': false,
                    'is_save_album_cover': false
                },
                musicInfo: {
                    'genre': '流行',
                    'is_save_lyrics_file': false,
                    'is_save_album_cover': false,
                    'source': ''
                },
                musicInfoManual: {
                    'genre': '流行',
                    'is_save_lyrics_file': false,
                    'is_save_album_cover': false,
                    'source': ''
                },
                fadeShowDir: false,
                fadeShowDetail: false,
                showTranslation: false,
                isLoading: false,
                loadingText: '',
                SongList: [],
                reloadImg: true,
                genreList: [
                    {'id': '流行', name: '流行'},
                    {'id': '摇滚', name: '摇滚'},
                    {'id': '说唱', name: '说唱'},
                    {'id': '民谣', name: '民谣'},
                    {'id': '电子', name: '电子'},
                    {'id': '爵士', name: '爵士'},
                    {'id': '纯音乐', name: '纯音乐'},
                    {'id': '金属', name: '金属'},
                    {'id': '世界音乐', name: '世界音乐'},
                    {'id': '新世纪', name: '新世纪'},
                    {'id': '古典', name: '古典'},
                    {'id': '独立', name: '独立'},
                    {'id': '氛围音乐', name: '氛围音乐'}
                ],
                languageList: [
                    {'id': '中文', name: '中文'},
                    {'id': '英文', name: '英文'},
                    {'id': '日文', name: '日文'},
                    {'id': '韩文', name: '韩文'},
                    {'id': '泰文', name: '泰文'},
                    {'id': '未知', name: '未知'}
                ],
                checkedIds: [],
                checkedData: [],
                selectAutoMode: 'strict_album',
                sourceList: ['netease'],
                overwritePolicy: 'overwrite_all',
                skipScraped: false,
                logVisible: false,
                scrapeLogs: [],
                summaryData: {},
                failedItems: [],
                successItems: [],
                skippedItems: [],
                historyFilter: 'all',
                tidyFormData: {
                    root_path: '/app/media/',
                    first_dir: 'artist',
                    second_dir: ''
                },
                exampleSetting1: {
                    primary: {
                        visible: false,
                        headerPosition: 'left'
                    }
                },
                isScraping: false,
                progressText: '',
                historyVisible: false,
                albumSearchVisible: false,
                albumSearchQuery: '',
                isAlbumSearching: false,
                scheduleVisible: false,
                scheduleConfig: {
                    enabled: false,
                    interval_hours: 1,
                    interval_unit: 'hours',
                    select_mode: 'strict_album',
                    overwrite_policy: 'overwrite_all',
                    source_list: ['netease'],
                    skip_scraped: true
                },
                albumSearchResults: null,
                albumList: [],
                selectedAlbum: null,
                timer: null,
                statsVisible: false,
                statsLoading: false,
                statsData: null,
                statsTab: 'albums',
                statsDetailData: null,
                statsBreadcrumb: [],
                statsRootPath: '',
                currentPlayingFile: '',
                currentLyrics: '',
                lyricsOffset: 0, // In seconds
                audioCurrentTime: 0,
                exampleSetting2: {
                    primary: {
                        visible: false,
                        headerPosition: 'left'
                    }
                },
                exampleSetting3: {
                    primary: {
                        visible: false,
                        headerPosition: 'left'
                    }
                },

                cookieStr: '',
                sortedField: localStorage.getItem('sortedField') ? JSON.parse(localStorage.getItem('sortedField')) : []
            }
        },
        computed: {
            ...mapGetters(['geFullPath', 'getShowHistory', 'getShowSchedule', 'getShowStats']),
            filePath: {
                get() {
                    if (this.geFullPath) {
                        console.log(this.geFullPath)
                        const fullPath = this.geFullPath
                        this.$store.commit('setFullPath', '')
                        this.$nextTick(() => {
                            this.handleSearchFile()
                        })
                        return fullPath
                    } else {
                        return '/app/media/'
                    }
                },
                set(value) {
                    this.$store.commit('setFullPath', value)
                }
            },
            filteredHistoryItems() {
                const all = [
                    ...this.successItems.map(i => ({ ...i, type: 'success' })),
                    ...this.failedItems.map(i => ({ ...i, type: 'failed' })),
                    ...this.skippedItems.map(i => ({ ...i, type: 'skipped' }))
                ].sort((a, b) => {
                    // Sort by display_time descending (newest first) - display_time is derived from updated_at
                    const timeA = a.display_time || ''
                    const timeB = b.display_time || ''
                    return timeB.localeCompare(timeA)
                })
                if (this.historyFilter === 'all') return all
                return all.filter(i => i.type === this.historyFilter)
            },
            audioSrc() {
                if (!this.currentPlayingFile) return ''
                return this.$api.Task.streamAudioUrl(this.currentPlayingFile)
            },
            lyricsLines() {
                // For backward compatibility - just text lines
                return this.parsedLyrics.map(l => l.text)
            },
            parsedLyrics() {
                if (!this.currentLyrics) return []
                const lines = this.currentLyrics.split('\n')
                const result = []
                for (const line of lines) {
                    // Match LRC format: [mm:ss.xx] or [mm:ss]
                    const match = line.match(/^\[(\d{2}):(\d{2})(?:[.:])(\d{2,3})?\](.*)$/)
                    if (match) {
                        const min = parseInt(match[1], 10)
                        const sec = parseInt(match[2], 10)
                        const ms = match[3] ? parseInt(match[3].padEnd(3, '0'), 10) : 0
                        // Apply offset here. If offset is +0.05s, we want the lyric to appear 0.05s LATER.
                        // So the lyric's time should be increased by offset.
                        const time = min * 60 + sec + ms / 1000 + this.lyricsOffset
                        const text = match[4].trim()
                        if (text.length > 0) {
                            result.push({ time, text })
                        }
                    } else {
                        // Non-timestamped line, skip metadata like [ar:Artist]
                        const text = line.replace(/\[.*?\]/g, '').trim()
                        if (text.length > 0 && !line.startsWith('[')) {
                            result.push({ time: -1, text })
                        }
                    }
                }
                // Sort by time
                return result.sort((a, b) => a.time - b.time)
            },
            currentLyricIndex() {
                if (!this.parsedLyrics.length) return -1
                const currentTime = this.audioCurrentTime
                // Find the last lyric that has started
                let idx = -1
                for (let i = 0; i < this.parsedLyrics.length; i++) {
                    if (this.parsedLyrics[i].time >= 0 && this.parsedLyrics[i].time <= currentTime) {
                        idx = i
                    }
                }
                return idx
            }
        },
        watch: {
            currentLyricIndex(newIdx) {
                // Auto-scroll to current lyric
                if (newIdx >= 0 && this.$refs['lyricLine' + newIdx]) {
                    this.$nextTick(() => {
                        const el = this.$refs['lyricLine' + newIdx]
                        const target = Array.isArray(el) ? el[0] : el
                        if (target && this.$refs.lyricsContainer) {
                            const container = this.$refs.lyricsContainer
                            const lineTop = target.offsetTop - container.offsetTop
                            const scrollTo = lineTop - container.clientHeight / 2 + target.clientHeight / 2
                            container.scrollTop = Math.max(0, scrollTo)
                        }
                    })
                }
            },
            getShowSchedule(val) {
                if (val) {
                    this.openScheduleDialog()
                    this.$store.commit('setShowSchedule', false)
                }
            },
            getShowHistory(val) {
                if (val) {
                    this.historyVisible = true
                    this.$store.commit('setShowHistory', false)
                }
            },
            getShowStats(val) {
                if (val) {
                    this.statsVisible = true
                    this.$store.commit('setShowStats', false)
                }
            },
            statsVisible(val) {
                if (val) {
                    this.loadStats()
                }
            },
            historyVisible(val) {
                if (val) {
                    this.loadHistory()
                }
            }
        },
        created() {
            this.handleSearchFile()
        },
        methods: {
            tpl(node, ctx) {
                // 如果在某些情况下 h 不能自动注入而报错，需将 h 参数写上；一般来说 h 默认是第一参数，但是现在改为第一参数会导致已经使用的用户都需要修改，所以先放在最后。
                // 如果 h 能自动注入则可以忽略 h 参数，无需写上，否则 h 参数会重复。
                const titleClass = node.selected ? 'node-title node-selected' : 'node-title ' + node.state
                if (node.title.length > 25) {
                    return <span>
                    <span class={titleClass} domPropsInnerHTML={node.title.slice(0, 25)}
                        onClick={() => {
                            this.nodeClickOne(node)
                        }}>
                    </span>
                    </span>
                } else {
                    return <span>
                    <span class={titleClass} domPropsInnerHTML={node.title.slice(0, 25)}
                        onClick={() => {
                            this.nodeClickOne(node)
                        }}>
                    </span>
                    </span>
                }
            },
            backDir() {
                this.filePath = this.backPath(this.filePath)
                // this.handleSearchFile()
            },
            backPath(path) {
                // 使用正则表达式匹配最后一个斜杠及其后面的内容
                const regex = /\/([^\/]+)\/?$/
                const match = regex.exec(path)

                // 如果匹配到了最后一个斜杠及其后面的内容
                if (match) {
                    // 截取掉最后一个斜杠及其后面的内容
                    const parentPath = path.slice(0, match.index)

                    // 返回回退后的路径
                    return parentPath
                }

                // 如果没有匹配到最后一个斜杠及其后面的内容，则返回原始路径
                return path
            },
            nodeClickOne(node) {
                if (node.icon === 'icon-folder') {
                    if (this.filePath.endsWith('/')) {
                        this.filePath = this.filePath + node.name
                    } else {
                        this.filePath = this.filePath + '/' + node.name
                    }
                    // this.handleSearchFile()
                } else {
                    if (node.children && node.children.length > 0) {
                        return
                    }
                    this.musicInfo = this.baseMusicInfo
                    this.fileName = node.name
                    const separator = this.filePath.endsWith('/') ? '' : '/'
                    this.fullPath = this.filePath + separator + node.name

                    // Set current playing file for the audio player
                    this.currentPlayingFile = this.fullPath
                    // Clear search results so player UI shows
                    this.SongList = []

                    this.$api.Task.musicId3({'file_path': this.filePath, 'file_name': node.name}).then((res) => {
                        console.log(res)
                        if (res.result) {
                            this.musicInfo = res.data
                            this.musicInfo.is_save_lyrics_file = false
                            this.musicInfo.is_save_album_cover = false
                            this.files1 = [
                                {
                                    name: 'cover.png',
                                    status: 'done',
                                    url: this.musicInfo.artwork
                                }
                            ]

                            // Load lyrics for the player
                            this.loadFileLyrics(this.fullPath)
                        } else {
                            this.$cwMessage(res.message, 'error')
                        }
                    })
                }
            },
            // checkbox
            nodeCheckTwo(node, checked) {
                console.log(node, checked)
                if (checked) {
                    this.musicInfo = this.baseMusicInfo
                    if (node.children && node.children.length > 0) {
                        this.checkedData = []
                        this.checkedIds = []
                        node.children.forEach(el => {
                            this.checkedData.push({
                                checked: el.checked,
                                icon: el.icon,
                                id: el.id,
                                name: el.name,
                                title: el.title
                            })
                            this.checkedIds.push(el.id)
                        })
                    } else {
                        this.checkedData.push({
                            checked: node.checked,
                            icon: node.icon,
                            id: node.id,
                            name: node.name,
                            title: node.title
                        })
                        this.checkedIds.push(node.id)
                    }
                } else {
                    if (node.children && node.children.length > 0) {
                        this.checkedData = []
                        this.checkedIds = []
                    } else {
                        const index = this.checkedIds.indexOf(node.id)
                        if (index !== -1) {
                            this.checkedData.splice(index, 1)
                            this.checkedIds.splice(index, 1)
                        }
                    }
                }
                console.log(this.checkedIds)
            },
            handleCopy(k, v, source) {
                if (source) {
                    this.musicInfo.source = source
                }
                if (k === 'lyric') {
                    const resurce = this.resource !== 'smart_tag' ? this.resource : v.resource
                    this.$api.Task.fetchLyric({'song_id': v.id, 'resource': resurce}).then((res) => {
                        if (res.result) {
                            this.musicInfo['lyrics'] = res.data
                        } else {
                            this.$cwMessage('未找到歌词', 'error')
                        }
                    })
                } else if (k === 'album_img') {
                    this.musicInfo[k] = v
                    this.files1 = [
                        {
                            name: 'cover.png',
                            status: 'done',
                            url: v
                        }
                    ]
                    this.reloadImg = false
                    this.$nextTick(() => {
                        this.reloadImg = true
                    })
                } else if (k === 'lyric_tran') {
                    this.musicInfo['lyrics'] = v
                } else {
                    this.musicInfo[k] = v
                }
            },
            copyAll(item) {
                console.log('DEBUG: copyAll item:', item)
                const s = item.source || ''
                this.handleCopy('title', item.name, s)
                this.handleCopy('year', item.year, s)
                this.handleCopy('lyric', item, s)
                this.handleCopy('album', item.album, s)
                this.handleCopy('artist', item.artist, s)
                this.handleCopy('album_img', item.album_img, s)
                this.musicInfo.source = s
            },
            nodeExpandedOne(node, expanded) {
            },
            // 查询网易云接口
            toggleLock(mode) {
                if (mode === 'title') {
                    if (!this.musicInfo.title) {
                        this.$cwMessage('标题不能为空', 'error')
                        return
                    }
                    this.showTranslation = false
                    this.fadeShowDetail = false
                    this.$api.Task.fetchId3Title({
                        title: this.musicInfo.title,
                        resource: this.resource,
                        full_path: this.fullPath
                    }).then((res) => {
                        this.fadeShowDetail = true
                        this.SongList = res.data
                        if (!res.data || res.data.length === 0) {
                            this.$cwMessage('未找到相关歌曲', 'warning')
                        }
                    })
                }
            },
            translation() {
                if (!this.musicInfo.lyrics) {
                    this.$cwMessage('歌词不能为空', 'error')
                }
                this.fadeShowDetail = false
                this.showTranslation = true
                this.$api.Task.translationLyc({
                    lyc: this.musicInfo.lyrics
                }).then((res) => {
                    this.showTranslation = true
                    this.translationText = res.data
                })
            },
            // 文件目录
            handleSearchFile() {
                this.fadeShowDir = false
                this.checkedData = []
                this.checkedIds = []
                this.$api.Task.fileList({'file_path': this.filePath, sorted_fields: this.sortedField}).then((res) => {
                    if (res.result) {
                        this.treeListOne = res.data
                        this.fadeShowDir = true
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                })
            },
            // 过滤搜索
            handleSearch() {
                this.$refs.tree1.searchNode(this.searchWord)
                const searchResult = this.$refs.tree1.getSearchResult()
                this.isEmpty = searchResult.isEmpty
            },
            // 保存音乐信息
            handleClick() {
                console.log(this.musicInfo)
                const separator = this.filePath.endsWith('/') ? '' : '/'
                const params = [{
                    'file_full_path': this.filePath + separator + this.fileName,
                    ...this.musicInfo
                }]
                this.isLoading = true
                this.$api.Task.updateId3({'music_id3_info': params}).then((res) => {
                    this.isLoading = false
                    if (res.result) {
                        this.$cwMessage('修改成功', 'success')
                        this.$store.commit('setHasMsg', true)
                    } else {
                        this.$cwMessage('修改失败', 'error')
                    }
                })
            },
            handleBatch() {
                this.$bkInfo({
                    title: '确认要批量修改？',
                    confirmLoading: true,
                    confirmFn: () => {
                        try {
                            this.isLoading = true

                            this.$api.Task.batchUpdateId3({
                                'file_full_path': this.filePath,
                                'select_data': this.checkedData,
                                'music_info': this.musicInfoManual
                            }).then((res) => {
                                this.isLoading = false
                                console.log(res)
                                if (res.result) {
                                    this.$cwMessage('修改成功', 'success')
                                }
                            })
                            return true
                        } catch (e) {
                            console.warn(e)
                            return false
                        }
                    }
                })
            },
            handleBatchAuto() {
                this.$bkInfo({
                    title: '确认要批量修改？',
                    confirmLoading: true,
                    confirmFn: () => {
                        try {
                            this.isLoading = true
                            this.musicInfoManual['select_mode'] = this.selectAutoMode
                            this.musicInfoManual['source_list'] = this.sourceList
                            this.musicInfoManual['overwrite_policy'] = this.overwritePolicy
                            this.musicInfoManual['skip_scraped'] = this.skipScraped
                            this.$api.Task.batchAutoUpdateId3({
                                'file_full_path': this.filePath,
                                'select_data': this.checkedData,
                                'music_info': this.musicInfoManual
                            }).then((res) => {
                                this.isLoading = false
                                console.log(res)
                                if (res.result) {
                                    // Start Polling
                                    const taskId = res.data.task_id
                                    this.gameover = false
                                    this.isScraping = true
                                    this.progressText = '开始刮削...'
                                    this.exampleSetting1.primary.visible = false

                                    this.timer = setInterval(() => {
                                        this.$api.Task.taskStatus({ task_id: taskId }).then(statusRes => {
                                            if (statusRes.result) {
                                                const status = statusRes.data
                                                if (status.state === 'PROGRESS') {
                                                    this.progressText = `正在刮削: ${status.filename} (${status.current}/${status.total})`
                                                } else if (status.state === 'SUCCESS') {
                                                    clearInterval(this.timer)
                                                    this.isScraping = false
                                                    this.progressText = ''

                                                    const result = status.result
                                                    this.scrapeLogs = result.logs || []
                                                    this.summaryData = result
                                                    this.failedItems = result.failed_items || []
                                                    this.successItems = result.success_items || []
                                                    this.skippedItems = result.skipped_items || []
                                                    this.logVisible = true
                                                    this.$store.commit('setHasMsg', true)
                                                    this.handleSearchFile()
                                                } else if (status.state === 'FAILURE' || status.state === 'REVOKED') {
                                                    clearInterval(this.timer)
                                                    this.isScraping = false
                                                    this.progressText = ''
                                                    this.$cwMessage('任务失败', 'error')
                                                }
                                            }
                                        })
                                    }, 1000)
                                } else {
                                    this.$cwMessage(res.message || '任务启动失败', 'error')
                                }
                            })
                            return true
                        } catch (e) {
                            console.warn(e)
                            return false
                        }
                    }
                })
            },
            handleJump(item) {
                // Use parent_path if available (from history), otherwise extract from full_path
                const parentPath = item.parent_path || (item.full_path ? item.full_path.substring(0, item.full_path.lastIndexOf('/')) : null)
                if (!parentPath) {
                    this.$cwMessage('无法获取文件路径', 'error')
                    return
                }
                this.filePath = parentPath
                this.logVisible = false
                this.historyVisible = false // Close history dialog

                this.fadeShowDir = false
                this.checkedData = []
                this.checkedIds = []
                this.$api.Task.fileList({ 'file_path': this.filePath, sorted_fields: this.sortedField }).then((res) => {
                    if (res.result) {
                        this.treeListOne = res.data
                        this.fadeShowDir = true

                        this.$nextTick(() => {
                            const targetNode = this.treeListOne.find(node => node.name === item.name || node.full_path === item.full_path)
                            if (targetNode) {
                                this.nodeClickOne(targetNode)
                                setTimeout(() => {
                                    this.toggleLock('title')
                                }, 500)
                            }
                        })
                    } else {
                        this.$cwMessage(res.message, 'error')
                    }
                })
            },
            openAlbumSearch() {
                this.albumSearchQuery = this.musicInfo.album || ''
                this.albumSearchResults = null
                this.albumList = []
                this.selectedAlbum = null
                this.albumSearchVisible = true
            },
            searchAlbum() {
                if (!this.albumSearchQuery) return
                this.isAlbumSearching = true
                this.selectedAlbum = null
                this.albumSearchResults = null
                const resource = this.resource || 'netease'
                this.$api.Task.searchAlbums({
                    resource: resource,
                    album_name: this.albumSearchQuery
                }).then(res => {
                    this.isAlbumSearching = false
                    if (res.result && res.data.length > 0) {
                        this.albumList = res.data
                    } else {
                        this.albumList = []
                        this.$cwMessage(res.message || '未找到专辑', 'warning')
                    }
                }).catch(e => {
                    this.isAlbumSearching = false
                    this.$cwMessage('搜索失败: ' + (e.message || 'Wait Timeout'), 'error')
                })
            },
            selectAlbum(album) {
                this.selectedAlbum = album
                this.isAlbumSearching = true
                const resource = this.resource || 'netease'
                this.$api.Task.fetchAlbumDetails({
                    resource: resource,
                    album_id: album.id
                }).then(res => {
                    this.isAlbumSearching = false
                    if (res.result) {
                        this.albumSearchResults = res.data
                    } else {
                        this.$cwMessage(res.message || '获取专辑详情失败', 'error')
                    }
                }).catch(e => {
                    this.isAlbumSearching = false
                    this.$cwMessage('获取专辑详情失败: ' + (e.message || 'Wait Timeout'), 'error')
                })
            },
            backToAlbumList() {
                this.selectedAlbum = null
                this.albumSearchResults = null
            },
            applyAlbumTrack(track) {
                // Apply metadata
                this.musicInfo.title = track.name
                this.musicInfo.artist = track.artist
                this.musicInfo.album = this.albumSearchResults.album_name
                this.musicInfo.albumartist = this.albumSearchResults.album_artist
                this.musicInfo.year = this.albumSearchResults.year
                this.musicInfo.album_img = this.albumSearchResults.album_img
                this.musicInfo.tracknumber = track.idx
                this.musicInfo.source = this.resource || 'netease' // Default to current resource

                // Update Cover Preview
                this.files1 = [{
                    name: 'cover.png',
                    status: 'done',
                    url: this.albumSearchResults.album_img
                }]
                this.reloadImg = false
                this.$nextTick(() => {
                    this.reloadImg = true
                })

                this.albumSearchVisible = false

                // Fetch Lyric
                const resource = this.resource || 'netease'
                this.$api.Task.fetchLyric({
                    'song_id': track.id,
                    'resource': resource
                }).then((res) => {
                    if (res.result) {
                        this.musicInfo.lyrics = res.data
                        this.$cwMessage('已应用元数据和歌词', 'success')
                    } else {
                        this.$cwMessage('已应用元数据，但歌词获取失败', 'warning')
                    }
                })
            },
            async handleAutoMatchScores() {
                const tracks = this.albumSearchResults.tracks
                // treeListOne is [{ children: [...] }]
                const root = this.treeListOne[0]
                if (!root || !root.children) {
                    this.$cwMessage('文件列表为空', 'warning')
                    return
                }
                const files = root.children // These are the files in the current folder

                const updates = []
                const separator = this.filePath.endsWith('/') ? '' : '/'

                // Matches to process
                const matches = []

                files.forEach(file => {
                    // Try to match file -> track
                    if (file.children) return // Skip folders

                    let matchedTrack = null
                    const fullPath = file.full_path || (this.filePath + separator + file.name)

                    // Clean filename for name matching
                    const cleanName = file.name
                        .replace(/\.[^.]+$/, '') // Remove extension
                        .replace(/^\d+-\d+[\s.\-_]+/, '') // Remove disc-track prefix like "1-07 "
                        .replace(/^\d+[\s.\-_]+/, '') // Remove track prefix like "07 "
                        .replace(/^\d+/, '') // Remove any remaining leading digits
                        .trim()
                        .toLowerCase()

                    // Helper: extract Chinese characters from a string
                    const extractChinese = (str) => {
                        const matches = str.match(/[\u4e00-\u9fa5]+/g)
                        return matches ? matches.join('') : ''
                    }

                    // Helper: normalize string - remove ALL punctuation, spaces, special chars
                    const normalize = (str) => {
                        return str.replace(/[^a-z0-9\u4e00-\u9fa5]/gi, '').toLowerCase()
                    }

                    // Method 1 (PRIORITY): Match by normalized name
                    if (cleanName) {
                        let bestScore = 0
                        let bestMatch = null
                        const fileNameNorm = normalize(cleanName)
                        const fileNameChinese = extractChinese(cleanName)

                        tracks.forEach(t => {
                            const trackName = (t.name || '').toLowerCase().trim()
                            if (!trackName) return

                            const trackNorm = normalize(trackName)
                            const trackChinese = extractChinese(trackName)
                            let score = 0

                            // Exact normalized match = highest score
                            if (fileNameNorm === trackNorm) {
                                score = 1000
                            } else if (fileNameNorm.includes(trackNorm) || trackNorm.includes(fileNameNorm)) {
                                // Normalized substring match (handles punctuation/space differences)
                                const matchLen = Math.min(fileNameNorm.length, trackNorm.length)
                                const maxLen = Math.max(fileNameNorm.length, trackNorm.length)
                                score = 600 + (matchLen / maxLen) * 100
                            } else if (fileNameChinese && trackChinese && (fileNameChinese.includes(trackChinese) || trackChinese.includes(fileNameChinese))) {
                                // Chinese characters match (handles extra English in filename)
                                const matchLen = Math.min(fileNameChinese.length, trackChinese.length)
                                const maxLen = Math.max(fileNameChinese.length, trackChinese.length)
                                score = 500 + (matchLen / maxLen) * 100
                            }

                            if (score > bestScore) {
                                bestScore = score
                                bestMatch = t
                                console.log(`[Match] "${file.name}" -> "${t.name}" (score=${score.toFixed(0)}, norm="${fileNameNorm}" vs "${trackNorm}")`)
                            }
                        })

                        // Require minimum score to avoid false positives
                        if (bestScore >= 30) {
                            matchedTrack = bestMatch
                        }
                    }

                    // Method 2 (FALLBACK): Match by track number if name matching failed
                    // ONLY for disc 1 - multi-disc albums (disc 2+) use name matching only
                    if (!matchedTrack) {
                        let discNum = 1
                        let fileNum = null
                        // Try disc-track format: "2-01" -> disc=2, track=1
                        const discTrackMatch = file.name.match(/^(\d+)-(\d+)/)
                        if (discTrackMatch) {
                            discNum = parseInt(discTrackMatch[1], 10)
                            fileNum = parseInt(discTrackMatch[2], 10)
                        } else {
                            // Fallback: just leading number "01" or "1"
                            const numMatch = file.name.match(/^(\d+)/)
                            if (numMatch) {
                                fileNum = parseInt(numMatch[1], 10)
                            }
                        }
                        // Only use track number fallback for disc 1
                        // For disc 2+, track number doesn't map to idx correctly
                        if (fileNum !== null && discNum === 1) {
                            matchedTrack = tracks.find(t => parseInt(t.idx, 10) === fileNum)
                            if (matchedTrack) {
                                console.log(`[Track# Fallback] "${file.name}" -> "${matchedTrack.name}" (track=${fileNum})`)
                            }
                        } else if (!matchedTrack) {
                            console.log(`[NO MATCH] "${file.name}" (disc=${discNum}, track=${fileNum})`)
                        }
                    }

                    if (matchedTrack) {
                        matches.push({
                            file: file,
                            fullPath: fullPath,
                            track: matchedTrack
                        })
                    }
                })

                if (matches.length === 0) {
                    this.$cwMessage('未找到可匹配的曲目 (按编号或文件名均无匹配)', 'warning')
                    return
                }

                this.$bkInfo({
                    title: `确认匹配 ${matches.length} 个文件？`,
                    subTitle: '即将应用元数据并抓取歌词',
                    confirmFn: async() => {
                        this.isLoading = true
                        this.isScraping = true
                        this.progressText = '开始匹配...'
                        const resource = this.resource || 'netease'
                        const total = matches.length

                        try {
                            for (let i = 0; i < matches.length; i++) {
                                const m = matches[i]
                                // Show progress in header bar (like auto-scrape)
                                const fileName = m.file.name.replace(/\.[^.]+$/, '')
                                this.progressText = `正在刮削: ${fileName} (${i + 1}/${total})`
                                console.log(`[Album Match] ${i + 1}/${total}: ${m.file.name} -> ${m.track.name}`)

                                let lyrics = ''
                                try {
                                    const res = await this.$api.Task.fetchLyric({
                                        'song_id': m.track.id,
                                        'resource': resource
                                    })
                                    if (res.result) {
                                        lyrics = res.data
                                    }
                                } catch (e) {
                                    console.warn('Lyrics fetch failed', e)
                                }

                                updates.push({
                                    file_full_path: m.fullPath,
                                    title: m.track.name,
                                    artist: m.track.artist,
                                    album: this.albumSearchResults.album_name,
                                    albumartist: this.albumSearchResults.album_artist,
                                    year: this.albumSearchResults.year,
                                    album_img: this.albumSearchResults.album_img,
                                    tracknumber: m.track.idx,
                                    lyrics: lyrics,
                                    genre: m.track.genre || this.albumSearchResults.genre || '',
                                    comment: '',
                                    discnumber: m.track.disc || null,
                                    is_save_lyrics_file: true,
                                    is_save_album_cover: true,
                                    source: resource
                                })
                            }
                            this.isScraping = false
                            this.progressText = ''

                            // Batch save
                            const res = await this.$api.Task.updateId3({'music_id3_info': updates})
                            this.isLoading = false
                            if (res.result) {
                                this.$cwMessage('批量匹配成功', 'success')
                                this.albumSearchVisible = false
                                this.$store.commit('setHasMsg', true)
                                this.handleSearchFile()
                            } else {
                                let msg = res.message
                                if (typeof msg === 'object') {
                                    msg = JSON.stringify(msg)
                                }
                                this.$cwMessage('部分失败: ' + msg, 'error')
                            }
                        } catch (e) {
                            this.isLoading = false
                            console.error(e)
                            this.$cwMessage('批量处理出错', 'error')
                        }
                    }
                })
            },
            handleTidy() {
                this.$bkInfo({
                    title: '确认要整理文件夹？',
                    confirmLoading: true,
                    confirmFn: () => {
                        try {
                            this.isLoading = true
                            this.tidyFormData['file_full_path'] = this.filePath
                            this.tidyFormData['select_data'] = this.checkedData
                            try {
                                this.$api.Task.tidyFolder(this.tidyFormData).then((res) => {
                                    this.isLoading = false
                                    if (res.result) {
                                        const movedCount = res.data.moved_unorganized_count || 0
                                        let msg = '文件夹整理完成！'
                                        if (movedCount > 0) {
                                            msg += ` 已将 ${movedCount} 个未整理文件夹/文件移动到 "未整理文件" 目录。`
                                            this.$bkInfo({
                                                type: 'success',
                                                title: '整理完成',
                                                subTitle: msg
                                            })
                                        } else {
                                            this.$cwMessage(msg, 'success')
                                        }
                                        this.exampleSetting2.primary.visible = false
                                        this.handleSearchFile()
                                    } else {
                                        this.$cwMessage('整理失败: ' + res.message, 'error')
                                    }
                                })
                            } catch (e) {
                                this.isLoading = false
                            }
                            return true
                        } catch (e) {
                            console.warn(e)
                            return false
                        }
                    }
                })
            },
            changeSorted(element) {
                if (this.sortedField.includes(element)) {
                    this.sortedField.splice(this.sortedField.indexOf(element), 1)
                } else {
                    this.sortedField.push(element)
                }
                const obj = JSON.stringify(this.sortedField)
                window.localStorage.setItem('sortedField', obj)
                this.handleSearchFile()
            },
            handleSettings() {
                const obj = JSON.stringify(this.showFields)
                window.localStorage.setItem('showFields', obj)
                window.localStorage.setItem('resource', this.resource)
            },
            handleRes(response) {
                if (response.result) {
                    this.musicInfo.album_img = response.data
                    return true
                } else {
                    return false
                }
            },
            handleResBatch(response) {
                if (response.result) {
                    this.musicInfoManual.album_img = response.data
                    return true
                } else {
                    return false
                }
            },
            openScheduleDialog() {
                this.scheduleVisible = true
                this.$api.Task.getScheduleConfig().then(res => {
                    if (res.result) {
                        this.scheduleConfig = res.data
                    }
                })
            },
            saveScheduleConfig() {
                this.$api.Task.updateScheduleConfig(this.scheduleConfig).then(res => {
                    if (res.result) {
                        this.$cwMessage('定时任务配置已保存', 'success')
                        this.scheduleVisible = false
                    }
                })
            },
            loadHistory() {
                this.$api.Task.getRecord({ page_size: 10000 }).then(res => {
                    if (res.result) {
                        const tasks = res.data.results.sort((a, b) => {
                            const timeA = new Date(a.updated_at || a.created_at).getTime()
                            const timeB = new Date(b.updated_at || b.created_at).getTime()
                            return timeB - timeA
                        })
                        // Filter preserves original order from API (sorted by -created_at)
                        this.successItems = tasks.filter(t => t.state === 'success').map(t => {
                            const rawTime = t.updated_at || t.created_at
                            const time = rawTime ? rawTime.replace('T', ' ').split('.')[0] : ''
                            return {
                                name: t.song_name ? `${t.artist_name} - ${t.song_name}` : t.filename,
                                msg: `${time} - ${t.full_path}`,
                                type: 'success',
                                parent_path: t.parent_path,
                                created_at: t.created_at,
                                display_time: time,
                                detail_msg: t.detail_msg || ''
                            }
                        })
                        this.failedItems = tasks.filter(t => t.state === 'failed' || t.state === 'fail').map(t => {
                            const rawTime = t.updated_at || t.created_at
                            const time = rawTime ? rawTime.replace('T', ' ').split('.')[0] : ''
                            return {
                                name: t.song_name ? `${t.artist_name} - ${t.song_name}` : t.filename,
                                msg: `${time} - ${t.full_path}`,
                                type: 'failed',
                                parent_path: t.parent_path,
                                created_at: t.created_at,
                                display_time: time,
                                error_msg: t.error_msg || '未知错误'
                            }
                        })
                        this.skippedItems = tasks.filter(t => t.state === 'skipped').map(t => {
                            const rawTime = t.updated_at || t.created_at
                            const time = rawTime ? rawTime.replace('T', ' ').split('.')[0] : ''
                            return {
                                name: t.song_name ? `${t.artist_name} - ${t.song_name}` : t.filename,
                                msg: `${time} - ${t.full_path}`,
                                type: 'skipped',
                                parent_path: t.parent_path,
                                created_at: t.created_at,
                                display_time: time,
                                error_msg: ''
                            }
                        })
                    }
                })
            },
            navigateToPath(item) {
                if (item && item.parent_path) {
                    this.filePath = item.parent_path
                    this.handleSearchFile()
                    // Close the history dialog if open
                    this.scheduleVisible = false
                }
            },
            loadStats() {
                if (!this.filePath) {
                    this.statsData = null
                    return
                }
                this.statsLoading = true
                this.statsData = null
                this.statsDetailData = null
                this.statsBreadcrumb = []
                this.statsRootPath = this.filePath
                this.$api.Task.mediaStats({ folder_path: this.filePath }).then((res) => {
                    this.statsLoading = false
                    if (res.result) {
                        this.statsData = res.data
                    } else {
                        this.$cwMessage(res.message || '加载统计失败', 'error')
                    }
                }).catch(() => {
                    this.statsLoading = false
                    this.$cwMessage('加载统计失败', 'error')
                })
            },
            navigateToStatsItem(item) {
                if (item && item.parent_path) {
                    this.filePath = item.parent_path
                    this.handleSearchFile()
                    this.statsVisible = false
                }
            },
            resetStatsView() {
                this.statsDetailData = null
                this.statsBreadcrumb = []
            },
            navigateBreadcrumb(idx) {
                if (idx < this.statsBreadcrumb.length - 1) {
                    // Navigate to that level
                    const crumb = this.statsBreadcrumb[idx]
                    if (crumb.type === 'root') {
                        this.resetStatsView()
                    } else if (crumb.type === 'artist') {
                        this.drillDownArtist(crumb.name, false)
                    } else if (crumb.type === 'album_artist') {
                        this.drillDownAlbumArtist(crumb.name, false)
                    }
                }
            },
            drillDownArtist(name, updateBreadcrumb = true) {
                this.statsLoading = true
                this.$api.Task.mediaStatsDetail({
                    folder_path: this.statsRootPath,
                    view_type: 'artist_albums',
                    name: name
                }).then((res) => {
                    this.statsLoading = false
                    if (res.result) {
                        this.statsDetailData = res.data
                        if (updateBreadcrumb) {
                            this.statsBreadcrumb = [{ type: 'artist', name: name, label: '🎤 ' + name }]
                        }
                    }
                }).catch(() => {
                    this.statsLoading = false
                })
            },
            drillDownAlbumArtist(name, updateBreadcrumb = true) {
                this.statsLoading = true
                this.$api.Task.mediaStatsDetail({
                    folder_path: this.statsRootPath,
                    view_type: 'album_artist_albums',
                    name: name
                }).then((res) => {
                    this.statsLoading = false
                    if (res.result) {
                        this.statsDetailData = res.data
                        if (updateBreadcrumb) {
                            this.statsBreadcrumb = [{ type: 'album_artist', name: name, label: '👥 ' + name }]
                        }
                    }
                }).catch(() => {
                    this.statsLoading = false
                })
            },
            drillDownAlbum(name) {
                this.statsLoading = true
                this.$api.Task.mediaStatsDetail({
                    folder_path: this.statsRootPath,
                    view_type: 'album_songs',
                    name: name
                }).then((res) => {
                    this.statsLoading = false
                    if (res.result) {
                        this.statsDetailData = res.data
                        // Add to breadcrumb if coming from artist view
                        if (this.statsBreadcrumb.length > 0 && this.statsBreadcrumb[this.statsBreadcrumb.length - 1].type !== 'album') {
                            this.statsBreadcrumb.push({ type: 'album', name: name, label: '📀 ' + name })
                        } else if (this.statsBreadcrumb.length === 0) {
                            this.statsBreadcrumb = [{ type: 'album', name: name, label: '📀 ' + name }]
                        }
                    }
                }).catch(() => {
                    this.statsLoading = false
                })
            },
            loadFileLyrics(filePath) {
                this.currentLyrics = ''
                this.$api.Task.getLyrics({ file_path: filePath }).then((res) => {
                    if (res.result) {
                        // Prefer embedded lyrics, fallback to lrc file
                        this.currentLyrics = res.data.embedded || res.data.lrc_file || ''
                    }
                }).catch(() => {
                    this.currentLyrics = ''
                })
            },
            adjustLyricsOffset(delta) {
                this.lyricsOffset += delta
            },
            applyLyricsOffset() {
                if (this.lyricsOffset === 0) return

                const lines = this.musicInfo.lyrics.split('\n')
                const newLines = lines.map(line => {
                    const match = line.match(/^\[(\d{2}):(\d{2})(?:[.:])(\d{2,3})?\](.*)$/)
                    if (match) {
                        const min = parseInt(match[1], 10)
                        const sec = parseInt(match[2], 10)
                        const ms = match[3] ? parseInt(match[3].padEnd(3, '0'), 10) : 0
                        let totalSeconds = min * 60 + sec + ms / 1000
                        totalSeconds += this.lyricsOffset

                        if (totalSeconds < 0) totalSeconds = 0

                        const newMin = Math.floor(totalSeconds / 60)
                        const newSec = Math.floor(totalSeconds % 60)
                        const newMs = Math.round((totalSeconds - newMin * 60 - newSec) * 1000)

                        const minStr = String(newMin).padStart(2, '0')
                        const secStr = String(newSec).padStart(2, '0')
                        const msStr = String(newMs).padStart(3, '0')
                        const text = match[4] // Preserve original spacing

                        return `[${minStr}:${secStr}.${msStr}]${text}`
                    }
                    return line
                })

                this.musicInfo.lyrics = newLines.join('\n')
                this.lyricsOffset = 0
                this.$cwMessage('已应用歌词偏移', 'success')
            },
            onAudioTimeUpdate(event) {
                this.audioCurrentTime = event.target.currentTime
            },
            onAudioLoaded(event) {
                console.log('Audio loaded, duration:', event.target.duration)
            },
            onAudioError(event) {
                console.error('Audio error:', event.target.error)
                console.error('Audio src was:', event.target.src)
                this.$cwMessage('音频加载失败，请检查文件格式或浏览器兼容性', 'error')
            }

        }
    }
</script>
<style lang="postcss">
    html, body {
        overscroll-behavior: none;
    }
.bk-table-header .custom-header-cell {
    color: inherit;
    text-decoration: underline;
    text-decoration-style: dashed;
    text-underline-position: under;
}

.music-item {
    cursor: pointer;
}

.music-item:hover {
    color: #1facdd;
}

.label1 {
    width: 80px;
}

.parent {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    grid-template-rows: repeat(1, 1fr);
    grid-column-gap: 0;
    grid-row-gap: 0;
    place-items: center;
    margin-bottom: 15px;
}

.title2 {
    font-weight: 500;
}

.song-card {
    display: flex;
    align-items: center;
    border-bottom: 1px solid #E2E2E2;
}

.song-card:hover {
    background: #E2E2E2;
}

.add-button {
    width: 24px;
    height: 24px;
    line-height: 20px;
    display: inline-block;
    background-color: transparent;
    border: 1px solid #ccc;
    border-radius: 5px;
    margin-left: 5px;
    font-size: 12px;
    color: rgb(97, 97, 97);
    text-align: center;
    cursor: pointer;
}

.delete-button {
    width: 24px;
    height: 24px;
    line-height: 20px;
    display: inline-block;
    background-color: transparent;
    border: 1px solid #ccc;
    border-radius: 5px;
    margin-left: 5px;
    font-size: 12px;
    color: rgb(63, 63, 63);
    text-align: center;
    cursor: pointer;
}

@media (max-width: 500px) {
    /* 在屏幕宽度小于400像素时应用的CSS规则 */
    .file-section {
        background: #fff;
        height: calc(100vh - 75px);
        overflow: scroll;
        width: 100vh;
        border: 1px solid #173769;
        margin: 10px 0 10px 10px;
        border-radius: 20px;
    }
    .edit-section {
        background: #fff;
        height: calc(100vh - 75px);
        overflow: hidden;
        overscroll-behavior: none;
        width: 100vh;
        border: 1px solid #173769;
        margin: 10px 10px 10px 10px;
        border-radius: 20px;
    }

    .resource-section {
        background: #fff;
        height: calc(100vh - 75px);
        width: 100vh;
        flex: 1;
        overflow: scroll;
        border: 1px solid #173769;
        margin: 10px 10px 10px 0;
        border-radius: 20px;
    }
}

@media (min-width: 400px) {
    /* 在屏幕宽度大于400像素时应用的CSS规则 */
    .file-section {
        background: #fff;
        height: calc(100vh - 75px);
        overflow: scroll;
        min-width: 400px;
        border: 1px solid #173769;
        margin: 10px 0 10px 10px;
        border-radius: 20px;
    }

    .edit-section {
        background: #fff;
        height: calc(100vh - 75px);
        overflow: hidden;
        overscroll-behavior: none;
        border: 1px solid #173769;
        margin: 10px 10px 10px 10px;
        border-radius: 20px;
    }

    .resource-section {
        background: #fff;
        height: calc(100vh - 75px);
        min-width: 400px;
        flex: 1;
        overflow: scroll;
        border: 1px solid #173769;
        margin: 10px 10px 10px 0;
        border-radius: 20px;
    }
}

.bk-form-checkbox {
    margin-right: 10px;
}

.success {
    color: #d1cfc5;
}

.failed {
    color: #ac354b;
}

.null {
    color: #333146;
}

button.bk-success {
    background-color: rgb(17, 64, 108) !important;
    border-color: rgb(17, 64, 108) !important;
}

button.bk-primary {
    background-color: rgb(17, 64, 108) !important;
    border-color: rgb(17, 64, 108) !important;
}

button.bk-button-text {
    background-color: transparent !important;
}

.bk-form-checkbox.is-checked .bk-checkbox {
    border-color: rgb(17, 64, 108) !important;
    background-color: rgb(17, 64, 108) !important;
    background-clip: border-box !important;
}

.bk-button-group .bk-button.is-selected {
    border-color: rgb(17, 64, 108) !important;
    color: rgb(17, 64, 108) !important;
}

.bk-button.bk-default:hover {
    border-color: rgb(17, 64, 108) !important;
    color: rgb(17, 64, 108) !important;
}

.bk-form-radio input[type=radio].is-checked {
    color: rgb(17, 64, 108) !important;
}

.bk-steps .bk-step.current .bk-step-icon, .bk-steps .bk-step.current .bk-step-number, .bk-steps .bk-step.current .bk-step-text {
    border-color: rgb(17, 64, 108) !important;
    background-color: rgb(17, 64, 108) !important;
}

.bk-steps .bk-step.done .bk-step-icon, .bk-steps .bk-step.done .bk-step-number, .bk-steps .bk-step.done .bk-step-text {
    border-color: rgb(17, 64, 108) !important;
    color: rgb(17, 64, 108) !important;
}

.bk-icon.icon-arrows-left-circle {
    color: rgb(17, 64, 108) !important;
}

.bk-icon.icon-arrows-right-circle {
    color: rgb(17, 64, 108) !important;
}

.bk-icon.icon-arrows-right-shape {
    color: rgb(17, 64, 108) !important;
}

.bk-icon.icon-arrows-right-shape:hover {
    color: #df4d40 !important;
}

.bk-icon.icon-arrows-left-shape:hover {
    color: #df4d40 !important;
}

.bk-icon.icon-arrows-down-shape:hover {
    color: #df4d40 !important;
}

::-webkit-scrollbar {
    width: 0;
    background-color: transparent;
}

::-webkit-scrollbar-thumb {
    background-color: #f4f5f0;
}

.isSelected {
    background-color: #ecf3fe;
}

.edit-item {
    display: flex;
    margin-bottom: 10px;
    align-items: center;
}

.can-copy {
    cursor: pointer;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* File state colors: black=unscraped, green=success, red=fail */
.node-title.success {
    color: #28a745 !important;
}

.node-title.fail {
    color: #dc3545 !important;
}
</style>
