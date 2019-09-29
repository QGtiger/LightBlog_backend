var Time = {
    // 获取当前时间戳
    getUnix: function(){
        var date = new Date();
        return date.getTime();
    },
    // 获取今天0：0的时间戳
    getTodayUnix: function(){
        var date = new Date();
        date.setHours(0);
        date.setMilliseconds(0);
        date.setMinutes(0);
        date.setSeconds(0);
        return date.getTime();
    },
    // 获取今年的1月1号0时0分的时间戳
    getYearUnix: function(){
        var date = new Date();
        date.setHours(0);
        date.setMilliseconds(0);
        date.setMinutes(0);
        date.setSeconds(0);
        date.setMonth(0);
        date.setDate(1);
        return date.getTime();
    },
    //获取月日
    getMonthDate: function(timestamp){
        var date = new Date(timestamp);
        var month = date.getMonth() + 1<10?'0'+(date.getMonth() + 1):date.getMonth() + 1;
        var day = date.getDate() <10?'0'+date.getDate():date.getDate();
        return month+"-"+day;
    },
    //获取标准年月日
    getLastDate: function(timestamp){
        var date = new Date(timestamp);
        var month = date.getMonth() + 1<10?'0'+(date.getMonth() + 1):date.getMonth() + 1;
        var day = date.getDate() <10?'0'+date.getDate():date.getDate();
        return date.getFullYear() + "-"+month+"-"+day;
    },
    //转换时间
    getFormatTime: function(time){
        var timestamp = time * 1000;
        var now = this.getUnix();
        var today = this.getTodayUnix();
        var year = this.getYearUnix();
        var timer = (now-timestamp)/1000;
        var tips = '';
        if(Math.floor(timer)<60){
            tips = '刚刚';
        }else if(timer<3600){
            tips = Math.floor(timer/60)+'分钟前';
        }else if(timer>=3600 && (timestamp-today>=0)){
            tips = Math.floor(timer/3600)+'小时前';
        }else if(timer/86400<=31){
            tips = Math.ceil(timer/86400)+'天前';
        }else if(timer/86400>31 && (timestamp-year>=0)){
            tips = this.getMonthDate(timestamp);
        }else{
            tips = this.getLastDate(timestamp);
        }
        return tips;
    }
}

//Vue.directive('time', {
//    bind: function(el, binding){
//        el.innerHTML = Time.getFormatTime(binding.value);
//        el.__timeout__ = setInterval(function(){
//            el.innerHTML = Time.getFormatTime(binding.value)
//        }, 6000);
//    },
//    unbind: function(){
//        clearInterval(el.__timeout__);
//        delete el.__timeout__;
//    }
//})