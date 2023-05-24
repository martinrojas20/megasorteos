
 function  g(l_numeros){
    $('#form_pago').on('submit', async function(event){            
        event.preventDefault();
        var cantidad = parseInt($('#cant').val()); 
        const document = $('#document').val();   
        if (cantidad <= 0){
            alert('Introduzca una cantidad mayor que cero');        
            }
        
        else{             
            numeros_list = [] ;       
            while(cantidad > 0){                
                if(!l_numeros.length) {
                    alert('Los numeros se agotaron!!!');
                    break;            
                }
                else{            
                    let ind_al = Math.floor(Math.random() * l_numeros.length );
                    let numero = l_numeros[ind_al];
                    l_numeros.splice(ind_al, 1);            
                    numeros_list.push(numero);
                    cantidad -= 1;
                }                
            }                   
            
            numeros_list = numeros_list.toString();               
            const quantity =  $('#cant').val();
            const numeros = numeros_list;   
                                    
            try {
                const response =  fetch('/sorteo1', {
                method: 'POST',
                headers:{contentType:'application/json'},
                body:JSON.stringify({'cantidad':quantity, 'numeros':numeros, 'documento':document})
                })                
                .then(res =>{
                        
                    if (res.redirected) {                                                
                        window.location = res.url
                    } else {
                        showLoginError()
                    }
                })               
                    
                
            } catch (error) {
                console.log(error) 
            }     
                        
        } 
    });
}



function enviar_num(){
    $('#form_buscar').on('submit', async function(event){            
        event.preventDefault();
        const numero = $('#numero').val();
        const documento = $('#document_n').val();
        try {
            const response =  fetch('/buscar', {
            method: 'POST',
            headers:{contentType:'application/json'},
            body:JSON.stringify({'numero':numero, 'documento':documento})
            })                
            .then(res =>{
                
                if (res.redirected) {                                                
                    window.location = res.url
                } 
                else{
                    alert('El número no está disponible')
                }
            })  
            
        
        } catch (error) {
        console.log(error) 
        } 
    });    
}





function  g2(l_numeros){
    $('#form_pago').on('submit', async function(event){            
        event.preventDefault();
        var cantidad = parseInt($('#cant').val()); 
        const document = $('#document').val();   
        if (cantidad <= 0){
            alert('Introduzca una cantidad mayor que cero');        
            }
        
        else{             
            numeros_list = [] ;       
            while(cantidad > 0){                
                if(!l_numeros.length) {
                    alert('Los numeros se agotaron!!!');
                    break;            
                }
                else{            
                    let ind_al = Math.floor(Math.random() * l_numeros.length );
                    let numero = l_numeros[ind_al];
                    l_numeros.splice(ind_al, 1);            
                    numeros_list.push(numero);
                    cantidad -= 1;
                }                
            }                   
            
            numeros_list = numeros_list.toString();               
            const quantity =  $('#cant').val();
            const numeros = numeros_list;   
                                    
            try {
                const response =  fetch('/sorteo2', {
                method: 'POST',
                headers:{contentType:'application/json'},
                body:JSON.stringify({'cantidad':quantity, 'numeros':numeros, 'documento':document})
                })                
                .then(res =>{
                        
                    if (res.redirected) {                                                
                        window.location = res.url
                    } else {
                        showLoginError()
                    }
                })               
                    
                
            } catch (error) {
                console.log(error) 
            }     
                        
        } 
    });
}



function enviar_num2(){
    $('#form_buscar').on('submit', async function(event){            
        event.preventDefault();
        const numero = $('#numero').val();
        const documento = $('#document_n').val();
        try {
            const response =  fetch('/buscar2', {
            method: 'POST',
            headers:{contentType:'application/json'},
            body:JSON.stringify({'numero':numero, 'documento':documento})
            })                
            .then(res =>{
                
                if (res.redirected) {                                                
                    window.location = res.url
                } 
                else{
                    alert('El número no está disponible')
                }
            })  
            
        
        } catch (error) {
        console.log(error) 
        } 
    });    
}







   
  

