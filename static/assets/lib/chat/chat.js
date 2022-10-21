
let smallChatBox = document.querySelector('.small-chat-box');
let parentChatBox = document.querySelector('.parent-chat-box');
let totalMessagesCountDiv=document.querySelector('.total-messages-count');

//Enable receiveing notifications
messaging.requestPermission()
        .then(() => {
            //When permissions granted
            if (!isTokenSentToServer()) {
                getRegistrationToken();
            } else {
                console.log("Token already generated");
            }
        })
        .catch((error) => {
            console.log(error);
        });
function getRegistrationToken() {
    console.log("In getting token");
    // Get Instance ID token. Initially this makes a network call, once retrieved
    // subsequent calls to getToken will return from cache.
    messaging.getToken().then((currentToken) => {
        if (currentToken) {
            sendTokenToServer(currentToken);

        } else {
            // Show permission request.
            console.log('No Instance ID token available. Request permission to generate one.');
            // Show permission UI.
            setTokenSentToServer(false);
        }
    }).catch((err) => {
        console.log('An error occurred while retrieving token. ', err);
        //showToken('Error retrieving Instance ID token. ', err);
        setTokenSentToServer(false);
    });
}
function setTokenSentToServer(sent) {
    window.localStorage.setItem('sentToServer', sent ? '1' : '0');
}
function isTokenSentToServer() {
    return window.localStorage.getItem('sentToServer') === '1';
}
function sendTokenToServer(currentToken) {
    console.log('Sending token to server...');
    // TODO(developer): Send the current token to your server.
    $.ajax({
        url: ajax_page,
        type: 'POST',
        data: {chatAction: 'saveUserChatToken', token: currentToken, user_id: user_id},
        success: function (html) {
            console.log(html);
            setTokenSentToServer(true);
        }
    });

}
messaging.onMessage((payload) => {
//    var notificationTitle = payload.data.title,
//            notificationOptions = {
//                body: payload.data.body,
//                icon: payload.data.icon
//            };
//    var notification = new Notification(notificationTitle, notificationOptions);
    try {
        var sender_id = document.querySelector('.recipient-id').value;
        if (payload.data.sender_id === sender_id) {
            var messageDiv = `<div class="left">
                            <div class="author-name"><small class="chat-date">${payload.data.time}</small></div>
                            <div class="chat-message active">${payload.data.body}</div>
                        </div>`;
            $('.small-chat-box .chat-content').append(messageDiv);
            scrollChatBottom();
        }else{
           var messages=totalMessagesCountDiv.innerHTML;
           
           messages=(messages)?parseInt(messages):0;
           totalMessagesCountDiv.innerHTML=messages+1;
        }
    } catch (error) {
        console.log(error);
    }
});


// Open close chat
$('.open-small-chat').click(function () {
    if (!parentChatBox.classList.contains('active')) {
        loadSystemUsers();
    }
    $(this).children().toggleClass('fa-comments').toggleClass('fa-remove');
    $('.parent-chat-box').toggleClass('active');
    $('.small-chat-box').removeClass('active');
});

let handleUserChats = function () {
    let userChats = document.querySelectorAll('.chat-user');
    for (var i = 0; i < userChats.length; i++) {
        const singleUserChat = userChats[i];
        singleUserChat.addEventListener('click', function () {
            if (!smallChatBox.classList.contains('active')) {
                smallChatBox.classList += ' active';
            }
            var sender_user_id = $(singleUserChat).attr("data-user-id"),
                    username = singleUserChat.querySelector('.user-name').innerHTML;
            smallChatBox.querySelector('.user-name').innerHTML = username;
            smallChatBox.querySelector('.recipient-id').value = sender_user_id;
            $.ajax({
                url: ajax_page,
                type: 'POST',
                data: {chatAction: 'loadSingleUserChat', user_id: user_id, other_user: sender_user_id},
                success: function (html) {
                    let chats = '';
                    try {
                        var data = jQuery.parseJSON(html);
                        data.forEach((chat) => {
                            chats += `<div class="${(chat.message_from === user_id) ? 'right' : 'left'}">
								<div class="author-name"><small class="chat-date">${chat.time_created}</small></div>
								<div class="chat-message ${(chat.message_from === user_id) ? 'right' : 'active'}">${chat.message}</div>
							</div>`;
                        });
                        smallChatBox.querySelector('.chat-content').innerHTML = chats;
                        scrollChatBottom();
                    } catch (err) {
                        console.log(err);
                    }
                }
            });
        });
    }
};
$('.chat-close-btn').click(function () {
    $('.small-chat-box').removeClass('active');
    document.querySelector('.recipient-id').value="";
});
const loadSystemUsers = function () {
    $.ajax({
        url: ajax_page,
        type: 'POST',
        data: {chatAction: 'loadOthersUsers', user_id: user_id},
        success: function (html) {
            let users = '';
            try {
                var data = jQuery.parseJSON(html);
                data.forEach((user) => {
                    user.photo = (user.photo) ? user.photo : default_avator;
                    users += `<div class="media chat-user" data-user-id="${user.id}">
				<div class="user-status status-offline"></div>
				<img class="align-self-center rounded-circle" src="${user.photo}" alt="">
				<div class="media-body">
					<h5><span class="user-name">${user.name}</span><span class="chat-timing">${user.last_sent}</span></h5>
					<p>${user.last_message}</p>
				</div>
			</div>`;
                });
                parentChatBox.querySelector('.chat-content').innerHTML = users;
                handleUserChats();
            } catch (err) {
                console.log(err);
            }
        }
    });
};
const sendChatMessageForm = document.querySelector('#send-chat-msg-form');
sendChatMessageForm.addEventListener('submit', function (event) {
    event.preventDefault();
    var messageBox = sendChatMessageForm.querySelector('.form-control'),
            recipient_id = sendChatMessageForm.querySelector('.recipient-id').value;
    var date = new Date();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    var strTime = hours + ':' + minutes + ':' + seconds + ' ' + ampm;
    var messageDiv = `
        <div class="right">
            <div class="author-name">You <small class="chat-date">${strTime}</small></div>
            <div class="chat-message">${messageBox.value}</div>
        </div>`;

    if (recipient_id) {
        $('.small-chat-box .chat-content').append(messageDiv);
        scrollChatBottom();
        $.ajax({
            url: ajax_page,
            type: 'POST',
            data: {chatAction: 'sendUserChatMessage', message: messageBox.value, message_from: user_id, message_to: recipient_id},
            success: function (html) {
                messageBox.value = '';
            }
        });
    }
});
function scrollChatBottom() {
    $(".small-chat-box .chat-content").animate({
        scrollTop: $('.small-chat-box .chat-content').height()
    }, 1000);
}
