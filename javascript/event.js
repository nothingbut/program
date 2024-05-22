/* Importing the EventEmitter class from the events module. */
var EventEmitter = require('events').EventEmitter;
var eventEmitter = new EventEmitter();

var listener1 = function listener1() {
    console.log("Listener1 executed.");
}

var listener2 = function listener2() {
    console.log("Listener2 executed.");
}

eventEmitter.addListener('connection', listener1);
eventEmitter.on('connection', listener2);

var eventListeners = eventEmitter.listenerCount('connection');
console.log(eventListeners + " Listener(s) listening to connection event.");

eventEmitter.emit('connection');

eventEmitter.removeListener('connection', listener1);
console.log("Listener1 will not listen now.");

eventEmitter.emit('connection');

var eventListeners = eventEmitter.listenerCount('connection');
console.log(eventListeners + " Listener(s) listening to connection event.");

console.log("Program Ended.");