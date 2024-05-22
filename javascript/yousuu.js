var requests = require('requests');
let id = 1;
const x = requests.get(`https://api.yousuu.com/api/book/${id}`);
const info = JSON.parse(x.text).data;

console.log(info)