(function ToolbarButtonMain()
{

const m_pluginId = "tb";
const errorHandler = err => AvNs.SessionError(err, m_pluginId);

AvNs.ViewMode = Object.freeze({
    DEFAULT: "",
    FREE: "_free"
});

function ToolbarButton()
{
    let m_viewMode = AvNs.ViewMode.DEFAULT;

    function getIconPath(iconId)
    {
        const paths = {};
        const sizes = ["19", "38"];
        for (const size of sizes)
        {
            const path = `/images/button/${iconId}_${size}.png`;
            paths[size] = browsersApi.extension.getURL(path);
        }
        return paths;
    }

    function GetValueExceptDefault(locales, key)
    {
        return locales[key] !== key ? locales[key] : null;
    }

    function GetByRegex(encoded, regex) 
    {
        let result = null;
        const match = encoded.match(regex);
        if (match && match.length > 1)
            result = match[1];
        return result;
    }

    function Base64ToBlob(encoded, mimeType)
    {
        const decoded = atob(encoded);
        const arrays = [];
        for (let offset = 0; offset < decoded.length; offset += 512)
        {
            const slice = decoded.slice(offset, offset + 512);
            const charCodes = new Array(slice.length);

            for (let i = 0; i < slice.length; i++)
                charCodes[i] = slice.charCodeAt(i);

            arrays.push(new Uint8Array(charCodes));
        }
        return new Blob(arrays, { type: mimeType });
    }

    function IsIconProvided(icon, id)
    {
        return icon && icon[id] && icon[id]["19"] && icon[id]["38"];
    }

    function CreateIconBitmap(image, size)
    {
        return new Promise(resolve =>
            {
                const encoded = image[size];
                const base64 = GetByRegex(encoded, /^\s*data:(?:[a-z]+\/[a-z0-9-+.]+(?:;[a-z-]+=[a-z0-9-]+)?)?(?:;base64)?,([a-z0-9!$&',()*+;=\-._~:@/?%\s]*?)\s*$/i);
                const mime = GetByRegex(encoded, /data:([a-zA-Z0-9]+\/[a-zA-Z0-9-.+]+).*,.*/);
                const blob = Base64ToBlob(base64, mime);
                createImageBitmap(blob, 0, 0, size, size).then(bitmap =>
                    {
                        resolve({ size: size, data: bitmap });
                    });
            });
    }

    function GetImageData(bitmap)
    {
        const canvas = new OffscreenCanvas(bitmap.size, bitmap.size);
        const context = canvas.getContext("2d");
        context.drawImage(bitmap.data, 0, 0);
        return context.getImageData(0, 0, bitmap.size, bitmap.size);
    }

    function GetIconDetails(iconId, resolve)
    {
        const iconIdFull = `${iconId}${m_viewMode}`;
        browsersApi.storage.local.get(["icon"], result =>
        {
            if (IsIconProvided(result.icon, iconIdFull))
            {
                Promise.all([
                    CreateIconBitmap(result.icon[iconIdFull], 19),
                    CreateIconBitmap(result.icon[iconIdFull], 38)
                ]).then(bitmaps => 
                {
                    const images = {};
                    for (const bitmap of bitmaps)
                        images[bitmap.size] = GetImageData(bitmap);

                    resolve({ imageData: images });
                });
            }
            else
            {
                resolve({ path: getIconPath(iconIdFull) });
            }
        });
    }

    function SetState(tabId, state)
    {
        ApiCall(browsersApi.browserAction.setBadgeText)
            .OnError(errorHandler)
            .Start({ tabId: tabId, text: state.badgeText || "" });

        if (state.badgeBackgroundColor) 
        {
            ApiCall(browsersApi.browserAction.setBadgeBackgroundColor)
                .OnError(errorHandler)
                .Start({ tabId: tabId, color: `#${state.badgeBackgroundColor}` });
        }

        GetIconDetails(state.iconId, details =>
            {
                details.tabId = tabId;
                ApiCall(browsersApi.browserAction.setIcon)
                    .OnError(errorHandler)
                    .Start(details);
            });
    }

    this.InitializeIcon = (locales, OnComplete) =>
    {
        if (locales && Boolean(Object.keys(locales).length))
        {
            browsersApi.storage.local.get(["icon"], result =>
            {
                if (!result.icon)
                {
                    browsersApi.storage.local.set({ 
                        icon: {
                            active: {
                                19: GetValueExceptDefault(locales, "ToolbarButtonActiveIcon_19"),
                                38: GetValueExceptDefault(locales, "ToolbarButtonActiveIcon_38")
                            },
                            inactive: {
                                19: GetValueExceptDefault(locales, "ToolbarButtonInactiveIcon_19"),
                                38: GetValueExceptDefault(locales, "ToolbarButtonInactiveIcon_38")
                            },
                            warning: {
                                19: GetValueExceptDefault(locales, "ToolbarButtonWarningIcon_19"),
                                38: GetValueExceptDefault(locales, "ToolbarButtonWarningIcon_38")
                            }
                        }
                    });
                }
                OnComplete();
            });
        }
        else
        {
            OnComplete();
        }
    };

    this.SetDefaultState = state =>
    {
        SetState(null, state);
        if (state.label)
        {
            ApiCall(browsersApi.browserAction.setTitle)
                .OnError(errorHandler)
                .Start({ title: state.label });
        }
    };

    this.SetTabState = args =>
    {
        const contextId = args.tabId;
        if (!AvNs.ValidateTabId(contextId))
            return;
        const tabIdParts = AvNs.SplitTabId(contextId);
        const tabId = tabIdParts.tabId;
        if (tabId > 1000)
            AvNs.SessionLog(`Get suspicious tab id ${tabId} from ${contextId}`, m_pluginId);

        ApiCall(browsersApi.tabs.get)
            .OnSuccess(() =>
                {
                    const state = args.buttonState ? args.buttonState : AvNs.JSONParse(args.state); 
                    if (!AvNs.HasValue(state.iconId))
                        state.iconId = "inactive";
                    SetState(tabId, state);
                })
            .OnError(err => AvNs.SessionLog(`Can't get tab ${tabId}, error: ${err.message}`, m_pluginId))
            .Start(tabId);
    };

    this.Reset = () =>
    {
        const manifest = browsersApi.runtime.getManifest();
        const title = manifest.browser_action ? manifest.browser_action.default_title : manifest.action.default_title;
        const factoryState = {
            badgeBackgroundColor: "000000", 
            label: title,
            iconId: "inactive"
        };
        this.SetDefaultState(factoryState);
    };

    this.SetMode = viewMode =>
    {
        m_viewMode = viewMode;
        this.Reset();
    };
}

var gToolbarButton = null;
AvNs.GetToolbarButton = function GetToolbarButton()
{
    if (!gToolbarButton)
        gToolbarButton = new ToolbarButton();

    return gToolbarButton;
};

function SetDefaultState(settings)
{
    const tb = AvNs.GetToolbarButton();
    if (AvNs.IsDefined(settings.defaultButtonState))
        tb.SetDefaultState(settings.defaultButtonState);
}

function OnPing()
{
    return AvNs.MaxRequestDelay;
}

function StartToolbarButtonController(ns, session, settings, locales)
{
    session.InitializePlugin((activatePlugin, registerMethod) =>
    {
        const tb = AvNs.GetToolbarButton();
        activatePlugin(m_pluginId, OnPing, StopToolbarButtonController);
        registerMethod("tb.setDefaultState", state =>
            {
                tb.SetDefaultState(state);
            });
        registerMethod("tb.setTabState", args =>
            {
                tb.SetTabState(args);
            });

        tb.InitializeIcon(locales, () => SetDefaultState(settings));
    });
}

function StopToolbarButtonController()
{
    try
    {
        AvNs.GetToolbarButton().Reset();
    }
    catch (e)
    {
        AvNs.SessionError(e, m_pluginId);
    }
}

AvNs.AddRunner2({
    name: m_pluginId,
    runner: StartToolbarButtonController,
    stop: StopToolbarButtonController
});

})();
