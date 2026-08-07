const chatArea = document.getElementById("chat-area");
const input = document.getElementById("message");
const button = document.getElementById("send-btn");

function createMessage(text, sender){

    const message=document.createElement("div");

    message.className=`message ${sender}`;

    const icon=sender==="user"
        ? "fa-user"
        : "fa-robot";

    message.innerHTML=`

        <div class="avatar">
            <i class="fa-solid ${icon}"></i>
        </div>

        <div class="bubble">${text}</div>

    `;

    chatArea.appendChild(message);

    chatArea.scrollTop=chatArea.scrollHeight;

}

async function sendMessage(){

    const text=input.value.trim();

    if(text==="") return;

    createMessage(text,"user");

    input.value="";

    const typing=document.createElement("div");

    typing.className="message bot";

    typing.innerHTML=`

        <div class="avatar">
            <i class="fa-solid fa-robot"></i>
        </div>

        <div class="bubble typing">
            Thinking...
        </div>

    `;

    chatArea.appendChild(typing);

    chatArea.scrollTop=chatArea.scrollHeight;

    try{

        const response=await fetch("/chat",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                message:text
            })

        });

        const data=await response.json();

        typing.remove();

        createMessage(data.reply,"bot");

    }

    catch{

        typing.remove();

        createMessage("Something went wrong.","bot");

    }

}

button.addEventListener("click",sendMessage);

input.addEventListener("keypress",(e)=>{

    if(e.key==="Enter"){

        sendMessage();

    }

});