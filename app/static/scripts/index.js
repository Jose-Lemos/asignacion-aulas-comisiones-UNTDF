
function getRandomArbitrary(min, max) {
    return Math.random() * (max - min) + min;
};

function addDig0(num){
    if (num < 10){
        return "0"+num;
    }else{
        return ""+num;
    }

}
// Función para insertar tareas en un rango de horas
function insertTask(startHour, startMinute, endHour, endMinute, day, comision) {
    const gridContainer = document.querySelector(".grid-container");
    
    //gridContainer.style.backgroundColor = colorRGB;
    switch (day) {
        case "Lunes":
            num_day = 1;
            break;
        case "Martes":
            num_day = 2;
            break;
        case "Miercoles":
            num_day = 3;
            break;
        case "Jueves":
            num_day = 4;
            break;
        case "Viernes":
            num_day = 5;
            break;
        case "Sabado":
            num_day = 6;
            break;
        case "Sabado":
            num_day = 6;
            break;
        default:
          console.log("Lo lamentamos, por el momento no disponemos de " + day + ".");
      }
    
    switch (startMinute) {
        case 29:
            startMinute = 30;
            break;
        case 59:
            startMinute = 0;
            startHour = startHour + 1;
            break;
    }

    switch (endMinute) {
        case 29:
            endMinute = 30;
            break;
        case 59:
            endMinute = 0;
            endHour = endHour + 1;
            break;
    }

    const startRowIndex = (startHour - 8) * 2 + (startMinute === 30 ? 1 : 0);
    const endRowIndex = (endHour - 8) * 2 + (endMinute === 30 ? 1 : 0);
    const col = num_day;
    let sum = (startRowIndex+endRowIndex);

    if (sum % 2 == 1){
        sum = sum+1;
    }
    const mid_row = sum/2;
    //console.log("midROw: "+mid_row);
    //const endColumnIndex = days.indexOf(dayEnd) + 1;
    let red = getRandomArbitrary(64, 255);
    let green = getRandomArbitrary(64, 255);
    let blue = getRandomArbitrary(64, 255);

    var colorRGB = 'rgb('+red+','+green+','+blue+')';

    for (let row = startRowIndex+1; row <= endRowIndex; row++) {
        const index = row * 8 + col;
        const taskCell = gridContainer.children[index];
        
        if (row == startRowIndex+1){
            taskCell.classList.add("bord-top");
        }
        //console.log("row:"+row);
        if (row == mid_row){
            // Crear un elemento <p> con texto
            const pElement = document.createElement("p");
            const texto = document.createTextNode(comision);
            pElement.appendChild(texto);
            taskCell.appendChild(pElement);
        }

        if (row == mid_row+1){
            // Crear un elemento <p> con texto
            const pElement = document.createElement("p");
            var txt = "";
            
            txt = ''+addDig0(startHour)+':'+addDig0(startMinute)+'hs - '+addDig0(endHour)+':'+ addDig0(endMinute)+'hs';
            
            
            const texto = document.createTextNode(txt);
            pElement.appendChild(texto);
            taskCell.appendChild(pElement);
        }

        if (row == endRowIndex){
            taskCell.classList.add("bord-bot");
        }

        taskCell.classList.add("task-filled");
        taskCell.classList.add("bord-lados");
        taskCell.style.backgroundColor = colorRGB;
    }
};

function get_horarios_comisiones_asignadas(){
    var comisionesBH_selector = document.getElementById("comBH-container");
    var cant_comBH = document.getElementById("cant-comisionesBH");

    console.log(comisionesBH_selector);
    console.log(cant_comBH);

    var hijos = comisionesBH_selector.children;
    
    for (var i = 0; i < hijos.length; i++) {
        //console.log(hijos[i].textContent);
        var cadena_comBH = ""+hijos[i].textContent;
        var list_comBH = cadena_comBH.split("#");
        //console.log(list_comBH);

        let hora_ini = 0;
        let minuto_ini = 0;
        let hora_fin = 0;
        let minuto_fin = 0;
        
        let dia = "";
        let comision = "";

        for (var j=0; j<list_comBH.length; j++){
            comision = list_comBH[0];
            dia = list_comBH[1];
            let hora_ini_cadena = list_comBH[2];
            let hora_fin_cadena = list_comBH[3];
            //console.log(comision, dia, hora_ini_cadena, hora_fin_cadena);
            let list_hora_ini = hora_ini_cadena.split(":");
            let list_hora_fin = hora_fin_cadena.split(":");

            

            for (var l=0; l<list_hora_ini.length; l++){  //obtenemos la hora y minuto de inicio
                hora_ini = parseInt(list_hora_ini[0]);
                minuto_ini = parseInt(list_hora_ini[1]);
            }

            for (var k=0; k<list_hora_ini.length; k++){  //obtenemos la hora y minuto de fin
                hora_fin = parseInt(list_hora_fin[0]);
                minuto_fin = parseInt(list_hora_fin[1]);
            }

            
        }
        // O realiza cualquier otra operación con cada hijo
        insertTask(hora_ini, minuto_ini, hora_fin, minuto_fin, dia, comision);
    };
    
};



function ocultarComisionesP(){
    var comisionesBH_selector = document.getElementById("comBH-container");
    comisionesBH_selector.style.display = 'none';
}

document.addEventListener("DOMContentLoaded", function () {
    const gridContainer = document.querySelector(".grid-container");
    
    // Generar las filas y columnas para las horas y días
    for (let hour = 8; hour <= 23; hour++) {
      const timeLabel = document.createElement("div");
      timeLabel.textContent = hour < 10 ? `0${hour}:00 hs` : `${hour}:00 hs`;
      timeLabel.classList.add("header");
      gridContainer.appendChild(timeLabel);

      
  
      for (let day = 0; day < 7; day++) {
        const taskCell = document.createElement("div");
        taskCell.classList.add("task");
        gridContainer.appendChild(taskCell);
      }

      if (hour != 23){
        const timeLabel1 = document.createElement("div");
        timeLabel1.textContent = hour < 10 ? `0${hour}:30 hs` : `${hour}:30 hs`;
        timeLabel1.classList.add("header");
        gridContainer.appendChild(timeLabel1);

        for (let day = 0; day < 7; day++) {
            const taskCell = document.createElement("div");
            taskCell.classList.add("task");
            gridContainer.appendChild(taskCell);
        }
      }
      
      
      
    }
    get_horarios_comisiones_asignadas();
    ocultarComisionesP();
  });
