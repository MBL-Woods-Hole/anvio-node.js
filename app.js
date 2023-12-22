const express=require("express"); 
const { exec, execSync, spawn } = require("child_process")
const fs   = require('fs');
const path = require('path');
const app= express();        //binds the express module to 'app'

//setting the view engine as EJS. 
app.set('view engine', 'ejs');
//roots the views directory to public
app.set('views', 'public');
//tells express that the public folder is the static folder
app.use(express.static("public"));
//home route

app.get("/", function(req,res){
  res.send("Welcome to the world of science fiction, conflicting theories, fantasies and some eccentric nerds!")
});

app.get("/anvio", function(req,res){
   
    console.log('In Anvio/:port')
    console.log('q',req.query)
    pg = req.query.pg
    if(!req.query.pg){
      pg = 'Veillonella_Atypica'
    }
    let PATH_TO_PANGENOMES = '/Users/avoorhis/programming/github/pangenomes'
    //
   //host_url = 'localhost:3010'
   // if(host_url == 'anvio.homd.org'){
//    
//    }else{
//    
//    }
    if(!req.query.port){
      return res.send("port not found")
    }
    let port = parseInt(req.query.port)
    if(!isInt(port)){
      return res.send("Bad port: '"+req.query.port+"'")
    }
    docker_params = ['exec','anvio','anvi-display-pan','-P',port,'-p',pg+'/PAN.db','-g',pg+'/GENOMES.db']
    
    docker_params.push('--server-only')
    docker_params.push('--debug')
    console.log('docker '+docker_params.join(' '))
    var out = fs.openSync(path.join(PATH_TO_PANGENOMES,'anvio.'+port+'.log'), 'w');
    var proc = spawn('/usr/local/bin/docker', docker_params, {
                    //env:{'PATH':CFG.PATH,'LD_LIBRARY_PATH':CFG.LD_LIBRARY_PATH},
                    detached: true, stdio: [ 'ignore', out, out ]  //, stdio: 'pipe'
                    //detached: false, stdio: 'pipe'  //, stdio: 'pipe'
     });
     proc.unref()  // this will allow proc to separate from node
     //console.log('proc',proc)
     //url = 'http://localhost:'+port
     //let url = 'http://localhost:3010/anvio?port='+port+'&pg='+pg
     let url = 'http://localhost:'+port
     //return res.send(url)
     res.render('pages/index', {
        title: 'HOMD :: ANVIO',
        pg: pg,
        port:port,
        url:url
     })
         
     
     //return res.send('Good port: '+port.toString())
   
});
function isInt(value) {
  return !isNaN(value) && 
         parseInt(Number(value)) == value && 
         !isNaN(parseInt(value, 10));
} 
// routing plot.ejs file
// this simply means calling localhost:3000/plot will render this page in our app
app.get("/plot", function(req,res){
  res.render("./pages/plot");
});

// routing cast.ejs file 
//this simply means calling localhost:3000/cast will render this page in our app
app.get("/cast", function(req,res){
  res.render("./pages/cast")
});

app.listen(3010, function(){
        console.log("SERVER STARTED ON localhost:3010");     
})