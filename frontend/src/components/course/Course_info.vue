<!-- Course_info page -->
<template>
  <div id="course_info">
    <Header></Header>
    <!-- course introduction -->
    <el-row :gutter="50" class="course_introduction">
        <el-col :span="18" >
            <el-button type="primary" icon = "d-arrow-left" @click="return_course_page_clicked" style="margin-top: 20px;margin-bottom: 10px">返回课程页面</el-button>
            <el-button type="primary" @click="enter_forum_clicked"style="float:right;margin-top: 20px; margin-bottom: 10px">进入课程论坛<i class="el-icon-d-arrow-right el-icon--right"></i></el-button>
          <div class="info_card">
            <el-card class="box-card">
            <div slot="header" class = "clearfix">
              <span style="line-height:45px;text-align: left;">
                <el-row>
                  <el-col :span="24">
                    <p style="padding-top:10px;font-size: xx-large;">{{ course_name }}</p>
                  </el-col>
                </el-row>
                <el-row>
                  <el-col :span="3">
                    <el-button type="primary" @click.native="course_like" v-if="liked" >取消收藏</el-button>
                    <el-button @click.native="course_like" v-else>收 藏</el-button>
                  </el-col>
                  <el-col :span="4">
                    收藏量： {{ like_count }}
                  </el-col>
                </el-row>
              </span>
            </div>
            <div>
              <div class="text item">
                授课教师: {{ teacher }}
              </div>
              <div class="text item">
                开课院系: {{ academy }}
              </div>
              <div class="text item">
                学时: {{ hours }}
              </div>
              <div class="text item">
                上课时间: {{ intro_info }}
              </div>
              <div class="text item">
                点击: {{ visit_count }}
              </div>
            </div>
            <div style="border-top: 1px solid silver;margin-top: 20px;padding-top: 20px;">
              <h1 style="font-weight:500;">成绩分析</h1>
              <div>
                <el-col :span="16">
                  <div id="pieReport" style="width: 550px;height: 400px;"></div>
                </el-col>
                <el-col :span="7">
                  <h2 style="margin-top: 50%; font-size: larger;">课程平均分: {{courseaverage}}</h2>
                </el-col>
              </div>

            </div>
          </el-card>
            
          </div>     
        </el-col>

      <!-- contribution rank -->
      <el-col :span="6" class = "contribution_container">
        <div class="contribution_table">
        <p style="text-align: center; padding-bottom: 10px"> 贡献度排行 </p>
        <el-table :data="contribution_data" highlight-current-row style="width: auto;" height="300">
          <el-table-column prop="contribution_username" label="用户名" align="center"></el-table-column>
          <el-table-column prop="contribution_score" label="贡献度" align="center"></el-table-column>
        </el-table>
        </div>
        <!--
        <div class="month_contribution_table">
        <p style="text-align: center; padding-bottom: 10px"> 近一个月贡献度排行 </p>
        <el-table :data="latest_contribution_data" highlight-current-row style="width: auto;" height="300">
          <el-table-column prop="contribution_username" label="用户名"></el-table-column>
          <el-table-column prop="contribution_score" label="贡献度"></el-table-column>
          <el-table-column prop="contribution_level" label="等级"></el-table-column>
        </el-table>
      </div>
    -->
      </el-col>
    </el-row>
     <!-- course resource -->

     <div class = "course_resource_container">
        <el-row class="course_resource_head" style="margin-bottom: 20px;margin-top: 50px;">
          <el-col :span="24" style="margin-top: 20px">
            <el-col :span="10">
              <p style="float: left;font-size: x-large">课程资源</p>
            </el-col> 
            <el-col :span="2" :offset="9">
              <el-button type="primary" icon="view" @click="check_all_resource_clicked" style="float: right;margin-right: 20px;">
                查看全部
              </el-button>
            </el-col> 
            <el-col :span="2" :offset="1">
              <el-button type="primary" icon="upload2" @click="uploadDialogVisible=true" style="float: right;">
                上传资源
              </el-button>
            </el-col> 
          </el-col>
      </el-row>
        <el-row class = "resource_container" >
          <el-col :span="16" class="hot_resource_container">
              <p style="text-align: left;padding-bottom: 20px;font-size: large"> 热门资源 </p>
          </el-col>
            <el-col :span="8" class= "latest_resource_container" :offset="14">
              <p style="padding-bottom: 10px; font-size: large">最新资源</p>
          </el-col>
        </el-row>
        <template v-for="(i,index) in total_resource_line">
              <el-row>
                <el-col :span="7" v-bind:style="{visibility:card_data[index][0].show}">
                  <el-col :span="24">
                    <el-tooltip effect="dark" :content="card_data[index][0].title" placement="top">
                  <el-button type="text" class="card_button" @click.native="card_clicked(index,0)">
                    <el-row>
                      <el-col :span="4" style="">
                        <img :src="card_data[index][0].img" style="width: 50px; height:50px;"></img>
                      </el-col>
                      <el-col :span="19" :offset="1">
                        <el-row >
                          <p class="card_title_text">{{card_data[index][0].title}}</p>
                        <p class="card_text">
                          上传者:{{card_data[index][0].uploader}}
                        </p>
                        <p class="card_text">
                          下载量:{{card_data[index][0].frequency}}
                        </p>
                      </el-row>
                      </el-col>
                    </el-row>
                </el-button>
              </el-tooltip>
              <hr style="border: none;border-top: 1px solid rgb(241,242,244)"/>
                </el-col>
                </el-col>

                <el-col :span="7" :offset="1" v-bind:style="{visibility:card_data[index][1].show}">
                  <el-col :span="24">
                  <el-tooltip effect="dark" :content="card_data[index][1].title" placement="top">
                  <el-button type="text" class="card_button" @click.native="card_clicked(index,1)">
                    <el-row>
                      <el-col :span="4" style="">
                        <img :src="card_data[index][1].img" style="width: 50px; height:50px;"></img>
                      </el-col>
                      <el-col :span="19" :offset="1">
                        <el-row >
                          <p class="card_title_text">{{card_data[index][1].title}}</p>
                        <p class="card_text">
                          上传者:{{card_data[index][1].uploader}}
                        </p>
                        <p class="card_text">
                          下载量:{{card_data[index][1].frequency}}
                        </p>
                      </el-row>
                      </el-col>
                    </el-row>
                </el-button>
              </el-tooltip>
              <hr style="border: none;border-top: 1px solid rgb(241,242,244)"/>
                </el-col>
                </el-col>
                <el-col :span="7" :offset="1" v-bind:style="{visibility:card_data[index][2].show}">
                  <el-tooltip effect="dark" :content="card_data[index][2].title" placement="top">
                  <el-button type="text" class="card_button" @click.native="card_clicked(index,2)">
                  
                    <el-row>
                      <el-col :span="4">
                        <img :src="card_data[index][2].img" style="width: 50px; height:50px;"></img>
                      </el-col>
                      <el-col :span="19" :offset="1">
                        <el-row >
                          <p class="card_title_text">{{card_data[index][2].title}}</p>
                        <p class="card_text">
                          上传者:{{card_data[index][2].uploader}}
                        </p>
                        <p class="card_text">
                          下载量:{{card_data[index][2].frequency}}
                        </p>
                      </el-row>
                      </el-col>
                    </el-row>
                </el-button>
              </el-tooltip>
              <hr style="border: none;border-top: 1px solid rgb(241,242,244)"/>
                </el-col>

      </el-row>
    </template>
    </div>
  <el-dialog title="上传资源" :visible.sync="uploadDialogVisible" size="tiny">
      <el-form label-position="left">
        <el-form-item type="text" label="资源介绍" :label-width="form_label_width">
          <el-input v-model="resourceIntro" auto_complete="off" placeholder="请输入资源介绍"></el-input>
        </el-form-item>
        <el-form-item :label-width="form_label_width">
          <input type="file" value="" id="file">
        </el-form-item>     
      </el-form>  
      <span slot="footer" class="dialog-footer">
        <el-button @click="uploadDialogVisible=false">取 消</el-button>
        <el-button type="primary" @click.native="upload">上 传</el-button>
      </span>      
    </el-dialog>

  <!-- 资源具体信息dialog -->
  <el-dialog title="资源信息" :visible.sync="dialogVisible" v-if="dialogVisible" size="small">
      <ResourceDialog></ResourceDialog>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible=false">取 消</el-button>
        <el-button type="primary" @click="dialogVisible = false">确 定</el-button>
      </span>
  </el-dialog>
  </div>

</template>

<script type="text/javascript">
/* eslint-disable camelcase */
/* eslint-disable space-infix-ops */
import echarts from 'echarts'
import Header from '../general/Header.vue'
import DocImg from './../../assets/fileico/docx_win.png'
import PdfImg from './../../assets/fileico/pdf.png'
import PptImg from './../../assets/fileico/pptx.png'
import JpgImg from './../../assets/fileico/jpeg.png'
import ZipImg from './../../assets/fileico/zip.png'
import RarImg from './../../assets/fileico/rar.png'
import ResourceDialog from '../general/ResourceDialog.vue'
import $ from 'jquery'
// 请不要删除和get_url相关的行，如果你真的需要请告诉我下原因。by xindetai
import get_url from '../general/getUrl.js'
import college_map from '../general/collegeMap.js'

// var echarts = require('echarts')
export default {
  name: 'course_info',
  components: { Header, ResourceDialog },

  beforeCreate () {
    var self = this
    var course_id = this.$route.params.course_id
    var post_url = get_url(this.$store.state.dev, '/course/course_info/')
    var postData = { 'course_id': course_id }
    $.ajax({
      ContentType: 'application/json; charset=utf-8',
      dataType: 'json',
      url: post_url,
      type: 'POST',
      data: postData,
      success: function (data) {
        var info = data['course_info']
        var college_id = info['college_id']
        var college_info = (college_map.hasOwnProperty(college_id)) ? college_map[college_id] : college_id.toString()
        self.course_name = info['name']
        self.teacher = info['teacher']
        self.academy = college_info
        self.hours = info['hours']
        var coursetime = ''
        if(info['XQ1'] != null){
          coursetime += info['XQ1']+' '
        }
        if(info['XQ2'] != null){
          coursetime += info['XQ2']+' '
        }
        if(info['XQ3'] != null){
          coursetime += info['XQ3']+' '
        }
        if(info['XQ4'] != null){
          coursetime += info['XQ4']+' '
        }
        if(info['XQ5'] != null){
          coursetime += info['XQ5']+' '
        }
        self.intro_info = coursetime
        self.$store.state.course_code = info['course_code']
      },
      error: function () {
        alert('fail')
      }
    })
    post_url = get_url(this.$store.state.dev, '/course/visit_count/')
    $.ajax({
      ContentType: 'application/json; charset=utf-8',
      dataType: 'json',
      url: post_url,
      type: 'POST',
      data: postData,
      success: function (data) {
        self.visit_count = data['visit_count']
      },
      error: function () {
        alert('点击次数链接异常')
      }
    })
    post_url = get_url(this.$store.state.dev, '/course/like/count/')
    $.ajax({
      ContentType: 'application/json; charset=utf-8',
      dataType: 'json',
      url: post_url,
      type: 'POST',
      data: postData,
      success: function (data) {
        self.liked = data['liked']
        self.like_count = data['like_count']
      },
      error: function () {
        alert('收藏量获取异常')
      }
    })
    /*
    // loading the contribution_list
    $.ajax({
      ContentType: 'application/json; charset=utf-8',
      dataType: 'json',
      url: get_url('')
    })
    */
    // loading the resource
  },
  data () {
    return {
      charts: "",
      studentnum:10,
      courseaverage:80,
      opinion: ["60分以下", "60~70分","70~80分","80~90分","90分以上"],
      opinionData: [
        { value: 12, name: "60分以下"},
        { value: 18, name: "60~70分"},
        { value: 12, name: "70~80分" },
        { value: 12, name: "80~90分"},
        { value: 12, name: "90分以上"},
      ],
      course_id: this.$route.params.course_id,
      like_count: 0,
      liked: false,
      course_name: '',
      teacher: '',
      academy: '',
      hours: '',
      intro_info: '',
      visit_count: -1,
      contribution_data: [],
      uploadDialogVisible: false,
      fileList: [],
      total_resource_line: 3,
      form_label_width: '80px',
      dialogVisible: false,
      resourceIntro: '',
      card_data: [
        [{ title: '', uploader: '', frequency: '', show: 'hidden', id: '', img: '' },
         { title: '', uploader: '', frequency: '', show: 'hidden', id: '', img: '' },
         { title: '', uploader: '', frequency: '', show: 'hidden', id: '', img: '' }],
        [{ title: '', uploader: '', frequency: '', show: 'hidden', id: '', img: '' },
         { title: '', uploader: '', frequency: '', show: 'hidden', id: '', img: '' },
         { title: '', uploader: '', frequency: '', show: 'hidden', id: '', img: '' }],
        [{ title: '', uploader: '', frequency: '', show: 'hidden', id: '', img: '' },
         { title: '', uploader: '', frequency: '', show: 'hidden', id: '', img: '' },
         { title: '', uploader: '', frequency: '', show: 'hidden', id: '', img: '' }]
      ],
      img: { zip: ZipImg,
        pdf: PdfImg,
        ppt: PptImg,
        pptx: PptImg,
        doc: DocImg,
        docx: DocImg,
        jpg: JpgImg,
        rar: RarImg
      }
    }
  },
  methods: {
    drawPie: function() {
      var mycharts = echarts.init(document.getElementById("pieReport"));
      // this.charts =  echarts.init(this.$refs.pieReport)
      mycharts.setOption({
        title: {
            text: '课程学生成绩分布',
            subtext: '数据样本总量：'+this.studentnum,
            // x 设置水平安放位置，默认左对齐，可选值：'center' ¦ 'left' ¦ 'right' ¦ {number}（x坐标，单位px）
            x: 'center',
            // y 设置垂直安放位置，默认全图顶端，可选值：'top' ¦ 'bottom' ¦ 'center' ¦ {number}（y坐标，单位px）
            y: 'top',
            // itemGap设置主副标题纵向间隔，单位px，默认为10，
            // itemGap: 30,
            // backgroundColor: '#EEE',
            // 主标题文本样式设置
            textStyle: {
              fontSize: 20,
              fontWeight: 'bolder',
              // color: '#000080'
            },
            // 副标题文本样式设置
            subtextStyle: {
              fontSize: 12,
              color: 'grey'
            }
          },
        tooltip: {
          trigger: "item",
          formatter: "{a}<br/>{b}:{c} ({d}%)"
        },
        legend: {
          bottom: 10,
          left: "center",
          data: this.opinion
        },
        series: [
          {
            name: "成绩分布",
            type: "pie",
            radius: "60%",
            center: ["50%", "50%"],
            avoidLabelOverlap: false,
            itemStyle: {
              emphasis: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)"
              },
              color: function(params) {
                //自定义颜色
                var colorList = ["rgb(46, 57, 58)", "#79d2c0", "rgb(28, 147, 168)", "rgb(179, 91, 119)","crimson"];
                return colorList[params.dataIndex];
              }
            },
            data: this.opinionData,
            label: {
              normal: {
                // position: 'inner',  // 设置标签位置，默认在饼状图外 可选值：'outer' ¦ 'inner（饼状图上）'
                // formatter: '{a} {b} : {c}个 ({d}%)'   设置标签显示内容 ，默认显示{b}
                // {a}指series.name  {b}指series.data的name
                // {c}指series.data的value  {d}%指这一部分占总数的百分比
                formatter: '{b}: {c} ({d}%)'
              }
            }
          }
        ]
      });
    },
    course_like: function () {
      var post_url = ''
      var post_data = { course_id: this.course_id }
      var _this = this
      if (!this.$store.state.is_login) {
        this.$message({
          showClose: true,
          type: 'error',
          message: '请先登录再收藏'
        })
        return
      }
      if (this.liked) {
        post_url = get_url(this.$store.state.dev, '/course/like/cancel/')
      } else {
        post_url = get_url(this.$store.state.dev, '/course/like/add/')
      }
      $.ajax({
        ContentType: 'application/json; charset=utf-8',
        dataType: 'json',
        url: post_url,
        type: 'POST',
        data: post_data,
        success: function (data) {
          if (_this.liked) {
            _this.$message({
              showClose: true,
              type: 'success',
              message: '取消成功'
            })
            _this.liked = false
            _this.like_count -= 1
          } else {
            _this.$message({
              showClose: true,
              type: 'success',
              message: '收藏成功'
            })
            _this.liked = true
            _this.like_count += 1
          }
        },
        error: function () {
          alert('收藏异常')
        }
      })
    },
    course_cancel_like: function () {

    },
    return_course_page_clicked: function () {
      this.$router.push({ path: '/course/' })
    },
    upload: function () {
      var formData = new FormData()
      var fileObj = document.getElementById('file').files[0]
      formData.append('file', fileObj)
      formData.append('name', fileObj.name)
      formData.append('only_url', false)
      formData.append('url', null)
      formData.append('intro', this.resourceIntro)
      formData.append('course_code', this.$store.state.course_code)
      var post_url = get_url(this.$store.state.dev, '/resourceUpload/')
      $.ajax({
        url: post_url,
        type: 'POST',
        data: formData,
        async: true,
        cache: false,
        contentType: false,
        processData: false,
        success: function (rdata) {
          rdata = JSON.parse(rdata)
          if (rdata['error'] === 0) {
            alert('上传文件成功！')
          } else {
            alert('上传失败！' + rdata['error'])
          }
        },
        error: function () {
          alert('fail')
        }
      })
    },
    edit_course: function () {
      this.$message({
        showClose: true,
        message: '功能暂未开放，敬请期待'
      })
    },
    submitUpload () {
      this.$refs.upload.submit()
    },
    handleRemove (file, fileList) {
      console.log(file, fileList)
    },
    handlePreview (file) {
      console.log(file)
    },
    check_all_resource_clicked: function () {
      this.$router.push({ path: 'resource/' })
    },
    enter_forum_clicked: function () {
      this.$router.push({ path: 'forum/' })
    },
    card_clicked (i, j) {
      this.$store.state.id = this.card_data[i][j].id
      var resourceDialogSelf = this
      var post_url = get_url(this.$store.state.dev, '/resource/information/')
      var _this = this
      $.ajax({
        ContentType: 'application/json; charset=utf-8',
        dataType: 'json',
        url: post_url,
        type: 'POST',
        async: false,
        data: {'resource_id': resourceDialogSelf.card_data[i][j].id},
        success: function (rdata) {
          resourceDialogSelf.$store.state.name = rdata['resource_info']['name']
          post_url = get_url(_this.$store.state.dev, '/user/information/')
          $.ajax({
            url: post_url,
            type: 'POST',
            data: {id: rdata['resource_info']['upload_user_id']},
            async: false,
            success: function (data) {
              data = JSON.parse(data)
              resourceDialogSelf.$store.state.author = data['user_info']['username']
            },
            error: function () {
              alert('fail')
            }
          })
          // resourceDialogSelf.$store.state.author = rdata['resource_info']['upload_user_id']
          resourceDialogSelf.$store.state.size = rdata['resource_info']['size']
          resourceDialogSelf.$store.state.time = rdata['resource_info']['upload_time']
          resourceDialogSelf.$store.state.intro = rdata['resource_info']['intro']
          resourceDialogSelf.$store.state.url = rdata['resource_info']['url']
          resourceDialogSelf.dialogVisible = true
        },
        error: function () {
          alert('拉取资源信息失败')
        }
      })
    }
  },
  mounted () {
    var course_id = this.$route.params.course_id
    var self = this
    var post_url = get_url(this.$store.state.dev, '/coursescore/')
    var post_data = {'courseid':course_id}
    $.ajax({
      ContentType: 'application/json; charset=utf-8',
      dataType: 'json',
      url: post_url,
      type: 'POST',
      data: post_data,
      async: false,
      success: function (data) {
        self.opinionData= data['studentscore']
        self.studentnum= data['studentnum']
        self.courseaverage= data['courseaverage']
      },
      error: function () {
        alert('连接服务器异常')
      }
    })
    this.drawPie();
    

    // latest resource
    var post_data = { 'course_id': course_id, 'number': this.total_resource_line }
    var self = this
    var post_url = get_url(this.$store.state.dev, '/resource/latest/')
    $.ajax({
      ContentType: 'application/json; charset=utf-8',
      dataType: 'json',
      url: post_url,
      type: 'POST',
      data: post_data,
      success: function (data) {
        var pos = 2 // pos of latest resource
        var info = data['result']
        for (var i = 0; i < info.length; i++) {
          self.card_data[i][pos].title=info[i]['name']
          self.card_data[i][pos].uploader=info[i]['username']
          self.card_data[i][pos].frequency=info[i]['download_count']
          self.card_data[i][pos].id = info[i]['resource_id']
          self.card_data[i][pos].show = 'visible'
          var name = info[i]['name'].toLowerCase()
          for (var t in self.img) {
            var temp = '.'+t+'$'
            var reg = new RegExp(temp)
            if (reg.test(name)) {
              self.card_data[i][pos].img = self.img[t]
              break
            }
          }
        }
      },
      error: function () {
        alert('拉取最新资源列表失败')
      }
    })
    // hot resource
    post_data = { 'course_id': course_id, 'number': this.total_resource_line*2 }
    post_url = get_url(this.$store.state.dev, '/course/resource/download/most/info/')
    $.ajax({
      ContentType: 'application/json; charset=utf-8',
      dataType: 'json',
      url: post_url,
      type: 'POST',
      data: post_data,
      success: function (data) {
        var info = data['info_list']
        for (var i = 0; i < info.length; i++) {
          var col = Math.floor(i % 2)
          var row = Math.floor(i / 2)
          self.card_data[row][col].title=info[i]['name']
          self.card_data[row][col].uploader=info[i]['username']
          self.card_data[row][col].frequency=info[i]['download_count']
          self.card_data[row][col].id = info[i]['resource_id']
          self.card_data[row][col].show = 'visible'
          var name = info[i]['name'].toLowerCase()
          for (var t in self.img) {
            var temp = '.'+t+'$'
            var reg = new RegExp(temp)
            if (reg.test(name)) {
              self.card_data[row][col].img = self.img[t]
              break
            }
          }
        }
      },
      error: function () {
        alert('拉取热门资源列表失败')
      }
    })
    // course contribution
    var post_url1 = get_url(this.$store.state.dev, '/course/contri/')
    var post_data1 = { course_id: this.$route.params.course_id }
    $.ajax({
      ContentType: 'application/json; charset=utf-8',
      dataType: 'json',
      url: post_url1,
      type: 'POST',
      data: post_data1,
      success: function (data) {
        var contri_list = data['contri_list']
        if (contri_list) {
          for (var i = 0; i < contri_list.length; i++) {
            var temp = {}
            temp.contribution_score = contri_list[i].contri
            temp.contribution_username = contri_list[i].username
            self.contribution_data.push(temp)
          }
        }
      },
      error: function () {
        self.$message({
          showClose: true,
          type: 'error',
          message: '无法连接到服务器'
        })
      }
    })
    /*
    var post_url2 = get_url(this.$store.state.dev, '/resource/hot/')
    var post_data2 = { course_id: this.$route.params.course_id, number: 6 }
    $.ajax({
      ContentType: 'application/json; charset=utf-8',
      dataType: 'json',
      url: post_url2,
      type: 'POST',
      data: post_data2,
      success: function (data) {
        var pos = 0
        var info = data['result']
        for (var i = 0; i < 3; i++) {
          self.card_data[i][pos].title=info[i]['name']
          self.card_data[i][pos].uploader=info[i]['username']
          self.card_data[i][pos].frequency=info[i]['download_count']
          self.card_data[i][pos].id = info[i]['resource_id']
          self.card_data[i][pos].show = 'visible'
          var name = info[i]['name'].toLowerCase()
          for (var t in self.img) {
            var temp = '.'+t+'$'
            var reg = new RegExp(temp)
            if (reg.test(name)) {
              self.card_data[i][pos].img = self.img[t]
              break
            }
          }
        }
        if (info.length > 3) {
          pos = 1
          for (i = 3; i < info.length; i++) {
            self.card_data[i][pos].title=info[i]['name']
            self.card_data[i][pos].uploader=info[i]['username']
            self.card_data[i][pos].frequency=info[i]['download_count']
            self.card_data[i][pos].id = info[i]['resource_id']
            self.card_data[i][pos].show = 'visible'
            var name1 = info[i]['name'].toLowerCase()
            for (var t1 in self.img) {
              var temp1 = '.'+t+'$'
              var reg1 = new RegExp(temp1)
              if (reg1.test(name1)) {
                self.card_data[i][pos].img = self.img[t1]
                break
              }
            }
          }
        }
      },
      error: function () {
        self.$message({
          showClose: true,
          type: 'error',
          message: '无法链接到服务器'
        })
      }
    })
    */
  }
}
</script>


<style type="text/css" scoped>
  .course_introduction{
    margin-top: 10px;
    padding-left: 20px;
    height: 100%;
    width: 100%;
  }
  .contribution_container{
    position:absolute;
    left:75%;
    margin-left: 10px;
  }
  .contribution_table{
    margin-bottom: 50px;
  }
  .item{
    padding-bottom: 5px;
  }
  .course_resource_container{
    /* position:absolute; */
    /* top:400px; */
    margin-top: 20px;
    padding-left: 20px;
    width: 71%;
  }
  .resource_container{
    width:auto;
  }
  .hot_resource_container{
    width:auto;
  }
  .latest_resource_container{
    width: auto;
  }
  .card_title_text:hover{
    color: #58B7FF;
  }
  .card_button{
    padding-top:0px;
    margin-top:0px;
    border:0px;
    width:100%;
    height:100%;
    text-align:left;
  }
  .card_title_text{
    padding-bottom: 10px;
    word-break: break-all;
    word-wrap: break-word;
    white-space: pre-wrap;
    color: black;
  }
  .card_text{
    color: grey;
  }
</style>