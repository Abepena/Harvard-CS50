document.addEventListener("DOMContentLoaded", () => {
    //establish a test namespace
    const namespace = '/test';

    // Connect to websocket
    let socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    // check for localstorage username
    if (!localStorage.getItem('username'))
        localStorage.setItem('username', '');

    else {
        socket.emit('submit_username', {
            "username": localStorage.getItem('username')
        })
    }

    // Disable the submit button by default
    document.querySelector("#submit").disabled = true;

    // Enabled only if there is text in field
    document.querySelector('#username').onkeyup = () => {

        if (document.querySelector("#username").value.length > 0) {
            document.querySelector("#submit").disabled = false;
        } else {
            document.querySelector("#submit").disabled = true;
        }
    }

    //When connected configure form
    socket.on('connect', () => {
        console.log("Websocket Connected")
    })

    //The submit button will emit a "submit_username" event
    document.getElementById('new-username').onsubmit = () => {
        //set username to a variable
        const username = document.getElementById("username").value;
        
        //set localstorage username
        localStorage.setItem('username', username)

        //emit username to server
        socket.emit('submit_username', {
            'username': username
        })
        //do not submit the form
        return false;
    };

    socket.on('username_response', data => {
        document.getElementById('user').innerHTML = data.username
       
        //Clear the input field and change the submit buttton text
        document.getElementById("username").value = ""
        document.getElementById("submit").value = "Change name";

        //Remove question
        document.getElementById("name-question").innerHTML = "";

        //disable button again
        document.getElementById("submit").disabled = true;

    })

    socket.on('message_response', msg => {
        let div = document.createElement('div')
        let t = document.createTextNode(`Message # ${msg.count}: ${msg.data}`)
        div.appendChild(t)
        document.querySelector('#log').appendChild(div)
    })

})