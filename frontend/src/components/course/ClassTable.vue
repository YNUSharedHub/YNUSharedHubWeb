<template>
  <!-- 课表组件 -->
  <div class="class-table">
    <div class="table-wrapper">
      <div class="tabel-container">
        <table>
          <thead>
            <tr>
              <th v-for="(item,index) in classTableData.weeks" :key="index">{{item?'周'+item:''}}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item,index) in classTableData.courses" :key="index">
              <td style="font-size:12px;background:#d4f7fd;word-wrap: break-word; 
  word-break: break-all; white-space: pre;">{{changeCharacter(index)}}</td>
              <td v-for="(innerItem,idx) in item" :key="idx" @click="toScanDetail(innerItem,idx)">
                <div style v-if="innerItem.lessonsName" :style="{background:colorArrays[idx%9]}">
                  <h4>{{innerItem.lessonsName}}</h4>
                  <p style="margin-top: 7px;">{{innerItem.lessonsAddress}}</p>
                  <p>{{innerItem.lessonsTeacher}}</p>
                  <p style="margin-top: 5px;">{{innerItem.lessonsRemark}}</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
  var that;
  import {
    Dialog
  } from "vant";
  export default {
    props: {
      classTableData: {
        type: Object
      }
    },
    data() {
      return {
        colorArrays: ['#ef8b9c', '#f15b6c', '#f26522', '#ffd400', '#8552a1', '#7fb80e', '#65c294', '#78cdd1',
          '#33a3dc'
        ]
      }
    },
    computed: {
      // 将数字转换成汉字
      changeCharacter(num) {
        return function (num) {
          var digArr = [1, 2, 3, 4, 5];
          var characterArr = [
            "1 2节\n\n8:30~10:10",
            "3 4节\n\n10:30~12:10",
            "5 6节\n\n14:00~15:40",
            "7 8节\n\n16:00~17:40",
            "9 10节\n\n19:00~20:40",
          ];
          return characterArr[num];
        };
      }
    },
    methods: {
      // 查看该课程的相关详情
      toScanDetail(item, idx) {
        // var con =
        //   `<div style="width:180px;text-align:left!important;margin:0 auto;color:#999;font-size:16px">课程名称：${item.lessonsName}<br/>上课时间：${item.lessonsTime}<br/>上课地点：${item.lessonsAddress}<br/>授课老师：${item.lessonsTeacher}<br/>课程课时：${item.lessonsRemark}</div>`;
        // if (item.lessonsName) {
        //   Dialog.alert({
        //     message: con
        //   });
        if (item.id) {
          this.$router.push({
            path: '../course/page/' + item.id
          })
        }
      }
    }
  }

</script>

<style scoped>
  .class-table {
    background-image: url("./cousretablepackground.png");
    /* background-size:; */
    background-repeat: no-repeat;
  }

  * {
    margin: 0;
    padding: 0;
  }

  .table-wrapper {
    width: 100%;
    overflow: auto;
    margin-bottom: 60px;
  }

  table {
    table-layout: fixed;
    width: 100%;
    border-collapse: collapse;
    color: #677998;
  }

  thead {
    background: #d4f7fd;
  }

  th {
    font-weight: bold;
    border-right: 2px solid #fefefe;
    border-bottom: 2px solid #fefefe;
    height: 46px !important;
  }

  tbody {
    font-size: 12px;
  }

  th,
  td {
    text-align: center;
    height: 120px;
    font-size: large;
    /* border-right: 1px solid #fefefe;
    border-bottom: 1px solid #fefefe; */
  }

  tr td div {
    /* background: #a5d16d; */
    width: 100%;
    height: 100%;
    color: #efefef;
    border-radius: 10px;
    padding: 15px;
    box-sizing: border-box;
  }

  tr td div p {
    font-size: smaller;
  }

  tr td:first-child {
    color: #333;
    font-weight: bold;
    border-right: 2px solid #fefefe;
    border-bottom: 2px solid #fefefe;
  }

  .course {
    background-color: #ebbbbb;
    color: #fff;
    display: inline-block;
    border-radius: 3px;
    width: 47%;
    margin: 1px 1%;
  }

  .bgColor {
    background-color: #89b2e5;
  }

</style>
