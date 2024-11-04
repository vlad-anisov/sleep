self.addEventListener("push", (event) => {

    console.log("GGWP")
    if (self.webkit){
        window.webkit.messageHandlers.bridge.postMessage("TEST2");
    }
    if (webkit){
        window.webkit.messageHandlers.bridge.postMessage("TEST3");
    }
        // event.data.json().options.body
});
