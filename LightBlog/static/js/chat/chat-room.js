$(function () {
    var socket = io.connect('http://39.108.219.55:2333/');

    var _username = null;

    var last_chat = new Date().getTime()-60001;

    //设置用户名

    _username = $(".username").val();
    if (_username) {
        socket.emit("login", {username: _username});
    }

    //发送消息
    var sendMessage = function () {
        var _message = $(".chatinput").val();

        if (_message) {
            socket.emit("sendMessage", {username: _username, message: _message});
        }
    };

    //自动补全两位，不足补0
    function fix(num, length) {
        return ('' + num).length < length ? ((new Array(length + 1)).join('0') + num).slice(-length) : '' + num;
      }

    // 获取时间
    function currentTime() {
        var d = new Date();
        if(d.getTime()-last_chat<60000){
            return '';
        }else{
            var str = '';
            // str += d.getFullYear() + '-';
            // str += d.getMonth() + 1 + '-';
            // str += d.getDate() + '  ';
            str += fix(d.getHours(),2) + ':';
            str += fix(d.getMinutes(),2)
            return str;
        }
    }

    //显示消息
    var showMessage = function (data) {
        if (data.username === _username) {
            $(".chat-content").append("" +
                "<div class='clearfloat'>" +
                "   <div class='time-column'>" +
                "       <small class='chat-date'>" + currentTime() + "</small>" +
                "   </div>" +
                "   <div class='right'>" +
                "       <div class='chat-nickname'>" + data.username + "</div>" +
                "       <div class='chat-message'>" + data.message + "</div>" +
                "       <div class='chat-avatars'><img src='/media/avator/"+data.username+".jpg'></div>" +
                "   </div>" +
                "</div>");
        } else {
            $(".chat-content").append("" +
                "<div class='clearfloat'>" +
                "   <div class='time-column'>" +
                "       <small class='chat-date'>" + currentTime() + "</small>" +
                "   </div>" +
                "   <div class='left'>" +
                "       <div class='chat-nickname'>" + data.username + "</div>" +
                "       <div class='chat-avatars'><img src='/media/avator/"+data.username+".jpg'></div>" +
                "       <div class='chat-message'>" + data.message + "</div>" +
                "   </div>" +
                "</div>");
        }
        last_chat = new Date().getTime();
    };

    //发送信息表单中回车触发 sendMessage();
    $("#chatinput").on("keyup", function (event) {
        if (event.keyCode === 13) {
            sendMessage();
            $("#chatinput").val(""); //清空
        }
    });


    //监听到登录成功后
    socket.on("loginSuccess", function (data) {
        if (data.username === _username) {
            layer.msg('Welcome...')
        }
    });

    //监听到事件发生就 显示消息
    socket.on("receiveMessage", function (data) {
        showMessage(data);
    });


});