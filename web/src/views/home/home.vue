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
                <div style="margin-left: 40px;width: 500px;margin-top: 20px;"
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
                        <div style="width: 70%;">
                            <bk-input :clearable="true" v-model="musicInfo.title"></bk-input>
                        </div>
                        <div>
                            <bk-icon type="arrows-right-shape" @click="toggleLock('title')"
                                style="cursor: pointer;color: #64c864;margin-left: 20px;">
                            </bk-icon>
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
                                    v-model="musicInfo.language"
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
                                <div>
                                    <bk-icon type="arrows-right-shape" @click="translation()"
                                        style="cursor: pointer;color: #64c864;margin-left: 20px;">
                                    </bk-icon>
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
                        <span style="margin-left: 30%;margin-top: 30%;">暂无歌曲信息</span>
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
                                    @click="handleCopy('album_img',item.album_img)">
                                </bk-image>
                            </div>
                            <div @click="handleCopy('title',item.name)" class="music-item">
                                <span v-if="item.source" :style="{ background: item.source === 'netease' ? '#c20c0c' : '#31c27c', color: 'white', padding: '1px 4px', borderRadius: '3px', fontSize: '10px', marginRight: '4px' }">{{ item.source === 'netease' ? '网易云' : 'QQ音乐' }}</span>
                                {{
                                    item.name
                                }}
                            </div>
                            <div @click="handleCopy('artist',item.artist)" class="music-item">
                                {{ item.artist }}
                            </div>
                            <div @click="handleCopy('album',item.album)" class="music-item">
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
                    <span style="margin-right: 8px;">
                        <bk-icon v-if="item.type === 'success'" type="check-circle-shape"></bk-icon>
                        <bk-icon v-else-if="item.type === 'failed'" type="close-circle-shape"></bk-icon>
                        <bk-icon v-else type="exclamation-circle-shape"></bk-icon>
                    </span>
                    {{ item.name }}
                </div>
            </div>
            <div v-else style="text-align: center; padding: 40px; color: #999;">
                暂无记录
            </div>
            <div style="margin-top: 15px; text-align: right;">
                <bk-button @click="historyVisible = false">关闭</bk-button>
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
                    'is_save_album_cover': false
                },
                musicInfoManual: {
                    'genre': '流行',
                    'is_save_lyrics_file': false,
                    'is_save_album_cover': false
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
            ...mapGetters(['geFullPath', 'getShowHistory', 'getShowSchedule']),
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
                    // Sort by created_at descending (newest first)
                    const timeA = a.created_at || ''
                    const timeB = b.created_at || ''
                    return timeB.localeCompare(timeA)
                })
                if (this.historyFilter === 'all') return all
                return all.filter(i => i.type === this.historyFilter)
            }
        },
        watch: {
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
                        }} v-bk-tooltips={node.title}>
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
            handleCopy(k, v) {
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
                this.handleCopy('title', item.name)
                this.handleCopy('year', item.year)
                this.handleCopy('lyric', item)
                this.handleCopy('album', item.album)
                this.handleCopy('artist', item.artist)
                this.handleCopy('album_img', item.album_img)
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

                    // Method 1 (PRIORITY): Match by song name (handles multi-disc albums correctly)
                    // Use best-score matching to avoid short names matching incorrectly
                    if (cleanName) {
                        let bestScore = 0
                        let bestMatch = null
                        tracks.forEach(t => {
                            const trackName = (t.name || '').toLowerCase().trim()
                            if (!trackName) return
                            let score = 0
                            // Exact match = highest score
                            if (cleanName === trackName) {
                                score = 1000
                            } else if (cleanName.includes(trackName)) {
                                // Track name is substring of filename - score by length ratio
                                score = (trackName.length / cleanName.length) * 100
                            } else if (trackName.includes(cleanName)) {
                                // Filename is substring of track name
                                score = (cleanName.length / trackName.length) * 100
                            }
                            if (score > bestScore) {
                                bestScore = score
                                bestMatch = t
                            }
                        })
                        // Require minimum score to avoid false positives
                        if (bestScore >= 30) {
                            matchedTrack = bestMatch
                        }
                    }

                    // Method 2 (FALLBACK): Match by track number if name matching failed
                    // Only use for single-disc albums or when name matching isn't possible
                    if (!matchedTrack) {
                        let fileNum = null
                        // Try disc-track format: "1-01" -> extract "01"
                        const discTrackMatch = file.name.match(/^\d+-(\d+)/)
                        if (discTrackMatch) {
                            fileNum = parseInt(discTrackMatch[1], 10)
                        } else {
                            // Fallback: just leading number "01" or "1"
                            const numMatch = file.name.match(/^(\d+)/)
                            if (numMatch) {
                                fileNum = parseInt(numMatch[1], 10)
                            }
                        }
                        if (fileNum !== null) {
                            matchedTrack = tracks.find(t => parseInt(t.idx, 10) === fileNum)
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
                    subTitle: `即将应用元数据并抓取歌词 (每首间隔 2秒 以防反爬，预计耗时 ${matches.length * 2}秒)`,
                    confirmFn: async() => {
                        this.isLoading = true
                        const resource = this.resource || 'netease'
                        const total = matches.length

                        try {
                            for (let i = 0; i < matches.length; i++) {
                                const m = matches[i]
                                // Show progress
                                const fileName = m.file.name.replace(/\.[^.]+$/, '')
                                this.loadingText = `正在处理: ${fileName} (${i + 1}/${total})`
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
                                    genre: '',
                                    comment: '',
                                    discnumber: null,
                                    is_save_lyrics_file: true,
                                    is_save_album_cover: true
                                })

                                // Wait 2s to be safe, except for the last one
                                if (i < matches.length - 1) {
                                    await new Promise(resolve => setTimeout(resolve, 2000))
                                }
                            }
                            this.loadingText = ''

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
                        const tasks = res.data.results
                        // Filter preserves original order from API (sorted by -created_at)
                        this.successItems = tasks.filter(t => t.state === 'success').map(t => {
                            const time = t.created_at ? t.created_at.replace('T', ' ').split('.')[0] : ''
                            return {
                                name: t.song_name ? `${t.artist_name} - ${t.song_name}` : t.filename,
                                msg: `${time} - ${t.full_path}`,
                                type: 'success',
                                parent_path: t.parent_path,
                                created_at: t.created_at
                            }
                        })
                        this.failedItems = tasks.filter(t => t.state === 'fail').map(t => {
                            const time = t.created_at ? t.created_at.replace('T', ' ').split('.')[0] : ''
                            return {
                                name: t.song_name ? `${t.artist_name} - ${t.song_name}` : t.filename,
                                msg: `${time} - ${t.full_path}`,
                                type: 'error',
                                parent_path: t.parent_path,
                                created_at: t.created_at
                            }
                        })
                        this.skippedItems = tasks.filter(t => t.state === 'skipped').map(t => {
                            const time = t.created_at ? t.created_at.replace('T', ' ').split('.')[0] : ''
                            return {
                                name: t.song_name ? `${t.artist_name} - ${t.song_name}` : t.filename,
                                msg: `${time} - ${t.full_path}`,
                                type: 'skipped',
                                parent_path: t.parent_path,
                                created_at: t.created_at
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
            }

        }
    }
</script>
<style lang="postcss">
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
        overflow: scroll;
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
        overflow: scroll;
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
