var smileyMenu = document.getElementById("smiley-menu");
var gifMenu = document.getElementById("giphy-menu");

function toggleAndCloseUserList() {
    var userList = document.getElementById('user-list');
    userList.style.display = userList.style.display === 'block' ? 'none' : 'block';
}

function filterUserList() {
    var searchTerm = document.getElementById('user-search').value.toLowerCase();
    var userListItems = document.querySelectorAll('#user-list ul li');
    userListItems.forEach(function (userListItem) {
        var user = userListItem.textContent.toLowerCase();
        var displayStyle = user.includes(searchTerm) ? 'block' : 'none';
        userListItem.style.display = displayStyle;
    });
}

function toggleSmileyMenu() {
    smileyMenu.style.display = (smileyMenu.style.display === "block") ? "none" : "block";
    // Close the gif menu when opening the smiley menu
    gifMenu.style.display = "none";
}

function addSmiley(smiley) {
    var messageInput = document.getElementById("message");
    messageInput.value += smiley;
    toggleSmileyMenu(); 
}

function toggleGifMenu() {
    gifMenu.style.display = (gifMenu.style.display === "block") ? "none" : "block";
    smileyMenu.style.display = "none";
}
function searchGifs() {
    var searchInput = document.getElementById("giphy-search");
    var searchTerm = searchInput.value;
    // Make a request to fetch GIFs
    fetch(`/get_gifs/${searchTerm}`)
        .then(response => response.json())
        .then(data => {
            console.log("Received data:", data);
            // the data
            displayGifs(data.gifs);
        })
        .catch(error => console.error("Error fetching GIFs", error));
}

function displayGifs(gifUrls) {
    var resultsDiv = document.getElementById("giphy-results");
    resultsDiv.innerHTML = "";
    gifUrls.forEach(url => {
        var img = document.createElement("img");
        var messageInput = document.getElementById("message");
        img.src = url;
        img.alt = "GIF";
        img.style.width = "50%";
        img.style.height = "50%";
        img.style.marginBottom = "5px";
        resultsDiv.appendChild(img);
        img.addEventListener('click', function() {
            // Add the GIF link to the message
            messageInput.value += `<img src="${img.src}" alt="GIF">`;
            sendMessage();
        });
    });
}

function openImageAttach() {
    var imageInput = document.getElementById("image-input");
    imageInput.click();
}

function handleImageInput(input) {
    const selectedImage = input.files[0];
    if (selectedImage) {
        const formData = new FormData();
        formData.append('image', selectedImage);
        //upload to IMGBB
        fetch('/upload_image', { method: 'POST', body: formData })
            .then(response => response.json())
            .then(({ image }) => {
                const messageInput = document.getElementById("message");
                messageInput.value += `<img src="${image}" alt="Uploaded Image">`;
                // Autosend
                sendMessage();
            })
            .catch(error => console.error("Error uploading image", error));
    }
}

document.addEventListener('click', function(event) {
    var target = event.target;
    // Check if the clicked element is outside smiley and GIF menus
    if (!target.closest('#smiley-menu') && !target.closest('#btn-smiley') &&
        !target.closest('#giphy-menu') && !target.closest('#btn-giphy')) {
        smileyMenu.style.display = "none";
        gifMenu.style.display = "none";
    }
});

////////////////////websocket/////////////////////
const socket = io();  // connect to the server

socket.on('connect', function() {
    console.log('Client connected.');
    var room_div = document.getElementById('chat');
    var room_id = room_div.getAttribute('room-id');
    console.log('Client emitting join_room:', room_id);
    socket.emit('join_room', { room_id: room_id });
});

function sendMessage() {
    var room_div = document.getElementById('chat');
    var room_id = room_div.getAttribute('room-id');

    var message = document.getElementById("message");
    var message_text = message.value;
    if(message_text != ''){ //do not send if message is empty
        console.log(room_id)
        socket.emit("new_message", { 'room_id': room_id, message: message_text });
        message.value = ''; // clear the input field
    }
}

socket.on('message', function(data) {  
    var msg = data.msg;
    var nasa_msg = DOMPurify.sanitize(msg);
    var user = data.user;
    var id = data.id
    var time_sent = data.time_sent;
    var img = data.img;
    var usr = user + "{{ }}";
    var li = document.createElement("li");
    li.classList.add(user.toLowerCase());
    li.classList.add('other-user');  // Add a class for styling initial messages differently
    var text = document.createTextNode(usr);
    li.appendChild(text);
    li.innerHTML = `<div class="user-profile">
                    <a href="/view_profile/${id}""><img src="${img}" alt="Profile Image" style="width: 30px; height: 30px; border-radius: 50%; margin-right: 10px;"></a>
                    </div>
                    <div class="message-content">
                        <span id="username" style="font-size: small; font-weight: bold;"><a style="text-decoration:none; color:white;" href="/view_profile/${id}">${user}</a> </span>
                        <span style="font-size: small; word-break: break-all;">${nasa_msg}</span>
                    </div>
                    <span class="timestamp">${time_sent}</span>`;

    var chatContainer = document.getElementById("chat");
    var isUserNearBottom = chatContainer.scrollHeight - chatContainer.clientHeight <= chatContainer.scrollTop + 1;
    document.getElementById("chat-messages").appendChild(li);
    if (isUserNearBottom) {
        setScrollToBottom();
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});

socket.on('disconnect', function() {
    var room_div = document.getElementById('chat');
    var room_id = room_div.getAttribute('room-id');
    socket.emit('leave_room', {room_id: room_id});
});

//Keycheck enter+shift
function keyCheck(event) {
    if(event.key === "Enter") {
        if(event.shiftKey) {  // check if Shift key is pressed
            // prevent default behavior
            event.preventDefault();
            // start a new line
            event.target.value = event.target.value + "\n";
        }
        else {
            event.preventDefault(); 
            sendMessage();
        }
    }
}