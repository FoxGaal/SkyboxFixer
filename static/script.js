
const data = {Image:[null],width:null,height:null,names:[null]}
let img_input = document.getElementById('image_input');
let file_input = document.getElementById('file_input');

const random_uuid = uuidv4();
const valid_pic_names = [
    "cubemap_0",
    "cubemap_1",
    "cubemap_2",
    "cubemap_3",
    "cubemap_4",
    "cubemap_5",
    "cube_back",
    "cube_right",
    "cube_front",
    "cube_left",
    "cube_up",
    "cube_down",
    "pz",
    "px",
    "nz",
    "nx",
    "py",
    "ny"
]

file_input.addEventListener('change', uploadImage);
function uploadImage(){
    if(file_input.files.length == 1) {
        let imageObj = new Image();
        imageObj.src = URL.createObjectURL(file_input.files[0]) 
        imageObj.onload = function () {
            console.log("purr");
            data.Image[0] = imageObj;
            data.width = imageObj.width;
            data.height = imageObj.height;
            UpdateCanvas();
        }
    } else {
        let imageObj = [];
        for(let i = 0; i < file_input.files.length; i++) {
            nameCheck = file_input.files[i].name
            let realName = false;
            
            for(let j = 0; j < valid_pic_names.length; j++) {
                if (nameCheck.replace(/\.[^/.]+$/, "")==valid_pic_names[j]) {
                    realName = true;
                    break;
                }
            }
            if(!realName) return;
            imageObj[i] = new Image();
            imageObj[i].src = URL.createObjectURL(file_input.files[i]) 
            data.Image[i] = imageObj[i];
            data.names[i] = nameCheck;
        }
        imageObj[5].onload = function() {
            data.width =  imageObj[5].width*3;
            data.height = imageObj[5].height*2;
            UpdateCanvas();
        }
    }
    
}

var percentage = 0;
var canvas = document.getElementById('output');
var context = canvas.getContext('2d');
var pic = document.getElementById('pic');
var drop = document.getElementById('drop');
var progress = document.getElementById('progress');
var completed = document.getElementById('completed');
var message = document.getElementById('status');

drop.addEventListener("dragover", function(e){
    e.preventDefault();
});
drop.addEventListener("drop", function(e){
    e.preventDefault();
    file_input.files = e.dataTransfer.files;
    uploadImage();
});

const style = function () {
    pic.style.height="100%";
    drop.textContent="";
    drop.style.border="0px";
    drop.style.backgroundColor="#00000000";
    drop.style.height="0";
    // drop.style.width="0";
    progress.style.width="100%";
    progress.style.height="50px";
    progress.style.padding="5px";
    progress.style.backgroundColor="#273541";
}
const UpdateCanvas = function() {
    if (!data.Image[0]) return;
        canvas.width = data.width;
        canvas.height = data.height;
        context.clearRect(0, 0, canvas.width, canvas.height);
    if(data.Image.length==1) {
        context.drawImage(data.Image[0], 0, 0);
    } else {
        let xsize = data.width/3;
        let ysize = data.height/2;
        for(let i=0; i < data.Image.length; i++) {
            let dx = 0, dy = 0;
            console.log(data.names[i].replace(/\.[^/.]+$/, ""))
            switch(data.names[i].replace(/\.[^/.]+$/, "")) {
                
                case "cubemap_0":
                case "cube_back":
                case "pz" :
                    dx=xsize;
                    dy=ysize;
                    break;
                case "cubemap_1" :
                case "cube_right":
                case "px" :
                    dx=xsize*2;
                    dy=ysize;
                    break;
                case "cubemap_2" :
                case "cube_front":
                case "nz" :
                    dx=xsize*2;
                    break;
                case "cubemap_3" :
                case "cube_left":
                case "nx" :
                    dy=ysize;
                    break;
                case "cubemap_4" :
                case "cube_up":
                case "py" :
                    dx=xsize;
                    break;
                case "cubemap_5" : 
                case "cube_down":
                case "ny" :
                    break;
            }
            context.drawImage(data.Image[i], dx, dy);
        }
    }
    
    style();
    download();
    setTimeout(function() {
        completed.style.height="100%";
      }, 2000);
};


var download = function(){
    var canvas = document.getElementById('output');
    var imageData = canvas.toDataURL('image/png'); // Convert canvas to Base64 string

    fetch('/upload-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image: imageData,
            id: random_uuid
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        } else {
            initiate_events();
        }
        return response.json();
    })
    .then(data => console.log('Image successfully uploaded:', data))
    .catch((error) => console.error('Error:', error));
}
let evtSource = null;
// const newElement = document.createElement("div");
// newElement.id = bar;
const initiate_events = function () {
    evtSource = new EventSource("/events?uuid="+random_uuid);
    evtSource.onopen = function(event) {
        console.log("Connection opened");
    };

    evtSource.onerror = function(event) {
        console.log("Error occurred", event);
    };
    

    evtSource.addEventListener("Rendered", function(event) {
        console.log(event.data);
        message.textContent="Rendered: "+event.data;
        percentage++;
        completed.style.width=100*(percentage/7)+"%";
        // newElement.textContent = event.data;
        // document.getElementById("events").appendChild(newElement);
        
        
    });
    evtSource.addEventListener("Started", function(event) {
        // document.getElementById("progress").appendChild(newElement);
        message.textContent=event.data;
        // document.getElementById("file_input").remove();
        console.log("Started");
    });
    evtSource.addEventListener("Finished", function(event, source=evtSource) {
        source.close();
        console.log("closed");
        message.textContent=event.data;
        percentage++;
        completed.style.width=100*(percentage/7)+"%";

        getpics();
    });
    evtSource.addEventListener("Error", function(event, source=evtSource) {
        source.close();
        console.log("closed");
        message.textContent=event.data;
    });
    
}

function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
    .replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0, 
            v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}
function getpics() {
    for (let download of document.getElementsByClassName('downloads')) {
        download.click();
    }
}