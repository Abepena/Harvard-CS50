document.addEventListener("DOMContentLoaded", () => {

    //emit event to server to add a channel
    document.querySelector("#add-channel").onsubmit = () => {
        let newChannelName = document.querySelector("#new-channel").value;
        socket.emit('add_channel', {
            "channel_name": newChannelName
        });
        return false;
    }

    //Create a new channel link on the channels page realtime 
    socket.on('add_channel_response', data => {
        let a = document.createElement('a')
        let t = document.createTextNode(`#${data.new_channel_name}`)
        a.appendChild(t)
        document.querySelector('#channels').appendChild(a)

        
    })

})