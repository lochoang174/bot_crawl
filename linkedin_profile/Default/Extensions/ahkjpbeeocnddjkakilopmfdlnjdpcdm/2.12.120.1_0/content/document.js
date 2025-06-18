let tabId = 0;

const docOptions = {
    name: "light_doc",
    runner: () => {},
    getParameters: () => ({
            tabId: tabId,
            scriptPluginId: Math.floor((1 + Math.random()) * 0x10000).toString(16) 
        })
};
AvNs.AddRunner2(docOptions);

function GetStartupParameters()
{
    ApiCall(browsersApi.runtime.sendMessage)
        .OnSuccess(response =>
            {
                if (!response)
                {
                    setTimeout(GetStartupParameters, 100);
                }
                else
                {
                    tabId = response.tabId;
                    if (response.isConnectedToProduct)
                        AvNs.StartSession();
                    else
                        setTimeout(GetStartupParameters, 2 * 60 * 1000);
                }
            })
        .OnError(err =>
            {
                setTimeout(GetStartupParameters, 100);
                const logFunction = err.message === "The message port closed before a response was received." ? AvNs.SessionLog : AvNs.SessionError;
                logFunction(`Error on GetStartupParameters: ${err.message}`, "light_doc");
            })
        .Start({ command: "getContentStartupParameters" });
}
GetStartupParameters();
