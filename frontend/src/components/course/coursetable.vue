<template>
  <div>
    <Header></Header>
    <div class="classtable">
      <v-ClassTable :classTableData="classTableData" />
    </div>
  </div>
</template>
<script>
  var that;
  import ClassTable from "./ClassTable";
  // import {
  //   reqFindTeacherLesson
  // } from "../../config/api";
  import Header from '../general/Header'
  import get_url from '../general/getUrl.js'
  import $ from 'jquery'

  export default {
    data() {
      return {
        msg: "",
        classTableData: {
          weeks: ["", "一", "二", "三", "四", "五", "六", "日"],
          courses: [],
        }
      };
    },
    components: {
      "v-ClassTable": ClassTable,
      Header
    },
    beforeCreate () {
      var self = this
      var post_url = get_url(this.$store.state.dev, '/getcoursetable/')
      var post_data = {"id":this.$store.state.userid}
      $.ajax({
        ContentType: 'application/json; charset=utf-8',
        dataType: 'json',
        url: post_url,
        type: 'POST',
        data: post_data,
        success: function (data) {
          console.log(data['respondlist'][1])
          self.classTableData.courses = data['respondlist']
          
        },
        error: function () {
          alert('获取课表信息失败')
        }
      })


      // const {
      //   userId,
      //   userName,
      //   roleId
      // } = JSON.parse(
      //   this.$cookie.get("userInfo")
      // );
      // this.findTeacherLesson(userName);
      // this.classTableData.courses = [
      //   [{
      //       "id": 1,  // 课程编号
      //       "classId": 2,   //学院编号
      //       "lessonsTime": "8:00-9:40",
      //       "lessonsName": "计算机导论",
      //       "lessonsAddress": "二教302",
      //       "lessonsTeacher": "吴老师",
      //       "lessonsRemark": "1-17周",
      //       "lessonsNumber": "1",   // 第几节课（1:12 2:34 3:56 4:78 5:910）
      //       "weekday": "星期一"
      //     },
      //     {
      //       "id": 19,
      //       "classId": 2,
      //       "lessonsTime": "8:00-9:40",
      //       "lessonsName": "编译原理",
      //       "lessonsAddress": "二教302",
      //       "lessonsTeacher": "吴老师",
      //       "lessonsRemark": "1-5,8-12周",
      //       "lessonsNumber": "1",
      //       "weekday": "星期四"
      //     },
      //     {}, {}, {},{}, {}
      //   ],    // 12节
      //   [{}, {}, {},{}, {},{}, {}],   // 34节
      //   [{}, {}, {},{}, {},{}, {}],   // 56节
      //   [{}, {}, {},{}, {},{}, {}],   // 78节
      //   [{}, {}, {},{}, {},{}, {}],   // 910节
      // ]
    },
    methods: {
      // 查询教师课表
      async findTeacherLesson(userName) {
        // that = this;
        // var params = {
        //   userName: userName
        // };
        // const { msg, status, info } = await reqFindTeacherLesson(params);
        // that.classTableData.courses = info;
      }
    }
  };

</script>

<style>
  .classtable {
    margin-left: 10%;
    margin-right: 10%;
  }

</style>
