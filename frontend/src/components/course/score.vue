<template>
  <div>
    <Header></Header>
    <div style="margin-left: 11%;">
      <HR style="margin-top: 50px; FILTER: alpha (opacity = 100, finishopacity =0 , style= 3 )" width="80%">
      <div style="margin-top: 40px;margin-bottom: 500px;margin-left: 30px;">
        <el-col :span="14">
          <div id="pieReport" style="width: 550px;height: 400px;"></div>
        </el-col>
        <!-- <el-col :span="1">
          <table border="1px" cellpadding="0" cellspacing="0"
            style=" margin-left :200 px ;height : 375px ; border-left-style: solid ; border-bottom-style : none; border-right-style :none ; border-top-style: none ">
          </table>
        </el-col> -->
        <el-col :span="9">
          <div class="seven_echarts" id="seven" style="width: 400px;height: 350px;margin-top: 20px;"></div>
        </el-col>
      </div>
      <HR style=" FILTER: alpha (opacity = 100, finishopacity =0 , style= 3 )" width="80%">
    </div>
  </div>
</template>

<script>
  import echarts from 'echarts'
  import Header from '../general/Header'
  import get_url from '../general/getUrl'
  import $ from 'jquery'

  export default {
    data() {
      return {
        gpalist:null,
        coursenum: 10,
        opinion: ["60分以下", "60~70分", "70~80分", "80~90分", "90分以上"],
        opinionData: [{
            value: 12,
            name: "60分以下"
          },
          {
            value: 18,
            name: "60~70分"
          },
          {
            value: 12,
            name: "70~80分"
          },
          {
            value: 12,
            name: "80~90分"
          },
          {
            value: 12,
            name: "90分以上"
          },
        ],
        seven_chart: null,
        month_chart: null,
        
      }
    },
    components: {
      Header
    },
    mounted() {
      var self = this
      var post_url = get_url(this.$store.state.dev, '/score/')
      var post_data = {'userid':this.$store.state.userid}
      $.ajax({
        ContentType: 'application/json; charset=utf-8',
        dataType: 'json',
        url: post_url,
        type: 'POST',
        data: post_data,
        async: false,
        success: function (data) {
          self.gpalist = data['gpa']
          self.opinionData= data['studentscore']
          self.coursenum= data['coursenum']
        },
        error: function () {
          alert('连接服务器异常')
        }
      })
      this.drawPie();
      this.get_echarts();
    },
    methods: {
      get_echarts: function () {
        this.seven_chart = echarts.init(document.getElementById("seven"));
        // 把配置和数据放这里
        this.seven_chart.setOption(
        {
          title: {
            text: 'GPA变化',
            x: 'left',
            align: 'center'
          },
          tooltip: {
            trigger: 'axis'
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          toolbox: {
            feature: {
              magicType: {
                type: ['line', 'bar']
              }, //柱状图和西和折线图切换
              restore: {}, //刷新
              saveAsImage: {}, //将图表以折线图的形式展现
            }
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: ["大一上", "大一下", "大二上", "大二下", "大三上", "大三下", "大四上"]
          },
          yAxis: {
            name: "GPA",
            nameLocation: 'end',
            type: 'value',
            axisLabel: {
              formatter: '{value} '
            }
          },
          series: [{
              name: 'GPA',
              type: 'line',
              data: this.gpalist,
              lineStyle: { //设置折线色颜色
                color: '#3f89ec'
              },
              itemStyle: { //设置折线折点的颜色
                normal: {
                  color: '#3f89ec'
                }
              }
            },


          ],
        }
        )
      },
      drawPie: function () {
        var mycharts = echarts.init(document.getElementById("pieReport"));
        // this.charts =  echarts.init(this.$refs.pieReport)
        mycharts.setOption({
          title: {
            text: '成绩分布',
            subtext: '数据样本总量：' + this.coursenum,
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
          series: [{
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
              color: function (params) {
                //自定义颜色
                var colorList = ["rgb(46, 57, 58)", "#79d2c0", "rgb(28, 147, 168)", "rgb(179, 91, 119)",
                  "crimson"
                ];
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
          }]
        });
      },
    }
  }

</script>

<style type="text/css">
  .content {
    width: 100%;
  }

  .content p {
    margin-top: 1rem;
    font-size: 0.4rem;
    color: #666666;
  }

  .seven_echarts {
    height: 11rem;
    width: 94%;
  }

</style>
