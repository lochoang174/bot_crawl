(function ExtensionMain()
{

const m_pluginId = "light_ext";
const errorHandler = err => AvNs.SessionError(err, m_pluginId);
const tabsReloadErrorHandler = err =>
    {
        if (err.message && err.message.startsWith("No current window"))
            AvNs.SessionLog("Failed reload active tab. No current window");
        else
            AvNs.SessionError(err, m_pluginId);
    };
const executeScriptErrorHandler = err =>
    {
        if (err.message && (err.message.startsWith("No tab with id") || err.message.startsWith("Invalid tab ID")))
            AvNs.SessionLog(`No tab found. Original error: ${err.message}`);
        else if (err.message && (err.message.startsWith("Invalid frame IDs") || err.message.startsWith("No frame with id")))
            AvNs.SessionLog(`No frame found. Original error: ${err.message}`);
        else if (err.message && (/Frame with ID \d+ is showing error page/).test(err.message))
            AvNs.SessionLog(`Failed execute script on error page. Original error: ${err.message}`);
        else if (err.message && (/Frame with ID \d+ was removed./).test(err.message))
            AvNs.SessionLog(`Failed execute script cause frame removed. Original error: ${err.message}`);
        else
            AvNs.SessionError(err, m_pluginId);
    };

function Extension()
{
    let m_queuedRequests = [];

    function OnSessionConnectedImpl(result)
    {
        try
        {
            AvNs.SessionLog(`Start light_ext session connection with result ${result}`);
            if (result !== 0)
                throw new Error(`Connect returned result=${result}`);

            AvNs.IsConnectedToProduct = true;
            AvNs.SessionLog(`${browsersApi.runtime.id}/${browsersApi.runtime.getManifest().version}/${navigator.userAgent.toString()} is online.`);

            browsersApi.runtime.onMessage.addListener(HandleRuntimeMessages);
            browsersApi.runtime.onMessage.removeListener(QueueRuntimeMessages);

            ProcessQueuedRuntimeMessages();

            AvNs.SessionLog("Finish light_ext session connection");
        }
        catch (e)
        {
            AvNs.SessionLog(e, m_pluginId);
            OnError(e);
        }
    }

    function OnPing()
    {
        return AvNs.MaxRequestDelay;
    }

    function OnError()
    {
        OnDisconnect();
    }

    function HandleRuntimeMessages(request, sender, sendResponse)
    {
        try
        {
            if (browsersApi.runtime.lastError)
            {
                AvNs.SessionLog(`Error on HandleRuntimeMessages: ${browsersApi.runtime.lastError.message}`, m_pluginId);
                return;
            }
            if (request.command === "reloadActiveTab")
            {
                if (AvNs.IsSenderPopup(sender))
                {
                    ApiCall(browsersApi.tabs.reload)
                        .OnError(tabsReloadErrorHandler)
                        .OnSuccess(() => AvNs.SessionLog("Reload active tab finished", m_pluginId))
                        .Start();
                }
            }
            else if (request.command === "getContentStartupParameters")
            {
                if (!sender.tab)
                {
                    AvNs.SessionLog(`sender.tab is undefined, wait for retry. Sender is: ${AvNs.JSONStringify(sender)}`, m_pluginId);
                    return;
                }

                AvNs.TrySendResponse(sendResponse, {
                    tabId: AvNs.EncodeTabId(sender.tab.windowId, sender.tab.id, sender.frameId),
                    isConnectedToProduct: AvNs.IsConnectedToProduct,
                    pluginId: browsersApi.runtime.id
                });
            }
        }
        catch (e)
        {
            AvNs.SessionError(e, m_pluginId);
        }
    }

    function ProcessQueuedRuntimeMessages()
    {
        for (const msg of m_queuedRequests)
            HandleRuntimeMessages(msg.request, msg.sender, msg.sendResponse);
        m_queuedRequests = [];
    }

    function OnDisconnect()
    {
        try
        {
            AvNs.Log("Connection with the product is lost.");
            AvNs.IsConnectedToProduct = false;

            browsersApi.runtime.onMessage.removeListener(HandleRuntimeMessages);
            browsersApi.runtime.onMessage.addListener(QueueRuntimeMessages);
        }
        catch (e)
        {
            AvNs.SessionError(e, m_pluginId);
        }
    }

    function QueueRuntimeMessages(request, sender, sendResponse)
    {
        try
        {
            if (browsersApi.runtime.lastError)
            {
                AvNs.SessionError(`Error on QueueRuntimeMessages for light ext with error: ${browsersApi.runtime.lastError.message}`, m_pluginId);
                return false;
            }

            m_queuedRequests.push({
                request: request,
                sender: sender,
                sendResponse: sendResponse
            });
            return true;
        }
        catch (e)
        {
            AvNs.SessionError(e, m_pluginId);
        }
    }

    function OnSessionConnected(settings, callFunction)
    {
        if (!settings.productVersion)
        {
            callFunction("light_ext.connect", [], OnSessionConnectedImpl, OnError); 
        }
        else
        {
            if (AvNs.IsDefined(settings.defaultButtonState) && AvNs.HasValue(settings.defaultButtonState.iconId))
                AvNs.GetToolbarButton().SetDefaultState(settings.defaultButtonState);
            OnSessionConnectedImpl(0);
        }
    }

    function InitializeToolbarButton(registerMethod, callFunction, locales, settings)
    {
        const tb = AvNs.GetToolbarButton();
        registerMethod("light_ext.setDefaultButtonState", state =>
            {
                tb.SetDefaultState(state);
            });

        registerMethod("light_ext.setButtonStateForTab", args =>
            {
                tb.SetTabState(args);
            });

        tb.InitializeIcon(locales, () => OnSessionConnected(settings, callFunction));
    }

    this.Start = (ns, session, settings, locales) =>
    {
        browsersApi.runtime.onMessage.addListener(QueueRuntimeMessages);
        ns.SessionLog("Start light_ext");
        AvNs.IsConnectedToProduct = false;

        session.InitializePlugin((activatePlugin, registerMethod, callFunction) =>
        {
            activatePlugin(m_pluginId, OnPing, OnError);

            registerMethod("light_ext.openNewTab", args =>
                {
                    ApiCall(browsersApi.tabs.create)
                        .OnError(errorHandler)
                        .Start({ url: args.url });
                });
            registerMethod("light_ext.reload", args =>
                {
                    if (!AvNs.ValidateTabId(args.tabId))
                        return;
                    const tabIdParts = AvNs.SplitTabId(args.tabId);
                    const reloadFunction = reloadArgs =>
                    {
                        if (reloadArgs.url && reloadArgs.url !== document.location.href)
                            window.history.pushState(0, document.title, reloadArgs.url);
                        document.location.reload(true);
                    };
                    ApiCall(browsersApi.tabs.executeScript)
                        .OnError(executeScriptErrorHandler)
                        .Start(
                            {
                                target: { tabId: tabIdParts.tabId, frameIds: [tabIdParts.frameId] },
                                func: reloadFunction,
                                args: [args]
                            }
                        );
                });

            InitializeToolbarButton(registerMethod, callFunction, locales, settings);
        });
    };

    this.Stop = () =>
    {
        OnDisconnect();
        AvNs.StopSession("stop");
    };
}

const extension = new Extension();

AvNs.AddRunner2({
    name: m_pluginId,
    runner: extension.Start,
    stop: extension.Stop
});
})();
