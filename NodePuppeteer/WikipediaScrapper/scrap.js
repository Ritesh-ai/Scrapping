const express = require('express');
const puppeteer = require('puppeteer')

var bodyParser = require('body-parser');

const app = express()
const port = 8001;

app.use(bodyParser.urlencoded({ extended: false }))
app.use(function (req, res, next) {

    // Website you wish to allow to connect
    res.setHeader('Access-Control-Allow-Origin', '*');

    // Request methods you wish to allow
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');

    // Request headers you wish to allow
    res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');

    // Set to true if you need the website to include cookies in the requests sent
    // to the API (e.g. in case you use sessions)
    res.setHeader('Access-Control-Allow-Credentials', true);

    // Pass to next layer of middleware
    next();
});

app.use(bodyParser.json({limit: '100mb'}));
app.use(bodyParser.urlencoded({limit: '100mb', extended: true}));

async function run(search1) {
    searchbar = search1.toLowerCase();
    console.log(searchbar);
    console.log("-----------------------------------------");
    const browser = await puppeteer.launch({
        headless: false
    });

    const page = await browser.newPage();
    const url = 'https://www.google.com/'
    await page.goto(url);
    const search = '#tsf > div:nth-child(2) > div > div.RNNXgb > div > div.a4bIc > input'
    const button_selector = '#tsf > div:nth-child(2) > div > div.FPdoLc.VlcLAe > center > input.gNO89b';
    await page.click(search);
    await page.keyboard.type(searchbar);
    await page.waitFor(2*1000);
    await page.keyboard.press('Enter');
    await page.waitFor(2*1000);

    const about = await page.$('[class="rc"]');
    let urls = await about.$eval(".r",
        (elements) => {
          let results = [];
          let items = document.querySelectorAll(".r");
          items.forEach((item) => {
            results.push({
              text: item.innerText
            });
          });
          return results;
        });
    var list = []
    urls.forEach(function(element) {
        var data = element["text"].split("\n")[1];
        if (data != undefined) {
            list.push(data);            
        }});
      var list1 = []
      list.forEach(function(element) {
        console.log(element+"-------------------------------------Element")
        var text = element.match('wikipedia.org');
        if (text!= null){
          console.log(element);
          list1.push(element);
        }
      });

      console.log(list1); 
      
      await page.goto(list1[0]);
      
      const wiki = await page.$('[id="mw-content-text"]');
      console.log(wiki);
      let ur = await wiki.$eval(
        ".mw-parser-output",
        (elements) => {
          // console.log(elements);
          let res1 = [];
          console.log("this worked");
          let items2 = document.querySelectorAll(".mw-parser-output > p");

          // return items2;
          items2.forEach((item2) => {
            // console.log(item2)
            res1.push({
              text: item2.innerText
            });
          });
          return res1;
        }
      );
      // console.log(ur);
      console.log([ur,list1]);
      return [ur,list1];
    }
  

app.post('/', function(req, res){
  // console.log(req);
  // For get method use the req.query.names for getting the parameter in the get method
  var names = req.body.names;
  console.log(names);
  console.log(typeof names);
  console.log("-------------------------------------------------")
  result = run(names)
  .then((result) => res.json(result))
});

app.listen(port, () => console.log(`Example app listening on port ${port}!`))
    
