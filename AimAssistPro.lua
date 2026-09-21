--[[
    ╔══════════════════════════════════════════════════════════════╗
    ║           AIM ASSIST PRO - FPS CLIENT SCRIPT                ║
    ║      Ultra-fast, zero-delay aim assist system               ║
    ║      Team detection | HP display | Off-After-Kill           ║
    ╚══════════════════════════════════════════════════════════════╝
    
    FEATURES:
      ✔ Zero-delay aim assist (Camera.Value + 1 RenderPriority)
      ✔ Team detection (skip allies, only aim enemies)
      ✔ Invincible/ForceField check (skip no-damage players)
      ✔ Off After Kill (auto-disable when ALL enemies in 150 stud die)
      ✔ Auto-reacquire (instantly re-lock if new enemy appears)
      ✔ Show HP billboards above enemy heads (color-coded)
      ✔ Target part selection (Head / Torso / HumanoidRootPart)
      ✔ FOV circle indicator
      ✔ Floating draggable GUI
      ✔ Minimize to animated circle
      ✔ Works even when enemy is off-screen
]]

-- ═══════════════════════════════════════════════════════════
-- SERVICES
-- ═══════════════════════════════════════════════════════════
local Players         = game:GetService("Players")
local RunService      = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local TweenService    = game:GetService("TweenService")
local Camera          = workspace.CurrentCamera

local LocalPlayer = Players.LocalPlayer
local Mouse       = LocalPlayer:GetMouse()

-- ═══════════════════════════════════════════════════════════
-- CONFIGURATION TABLE
-- ═══════════════════════════════════════════════════════════
local Config = {
    AimAssist = {
        Enabled       = false,
        MaxDistance   = 150,       -- stud radius
        Smoothness    = 0.04,      -- 0.01 = nearly instant, 0.5 = slow
        FOVRadius     = 250,       -- screen pixels FOV
        TargetPart    = "Head",    -- "Head" | "HumanoidRootPart" | "Torso"
        Priority      = "Nearest", -- "Nearest" | "LowestHP" | "OnScreen"
        TeamCheck     = true,      -- skip teammates
        NoDmgCheck    = true,      -- skip invincible / ForceField players
        OffAfterKill  = false,     -- auto-off when all 150-stud enemies dead
        AutoReacquire = true,      -- auto re-lock new enemy that enters range
    },
    ShowHP = {
        Enabled   = false,
        StudsOffset = Vector3.new(0, 3.2, 0),
        TextSize  = 15,
        AlwaysOnTop = true,
    },
    FOVCircle = {
        Visible   = true,
        Color     = Color3.fromRGB(255, 255, 255),
        Thickness = 1.5,
    },
    GUI = {
        AccentColor  = Color3.fromRGB(60, 130, 255),
        BgColor      = Color3.fromRGB(13, 13, 20),
        PanelColor   = Color3.fromRGB(22, 22, 33),
        TextColor    = Color3.fromRGB(230, 230, 240),
        Width        = 355,
        Height       = 490,
    },
}

-- ═══════════════════════════════════════════════════════════
-- STATE
-- ═══════════════════════════════════════════════════════════
local State = {
    AimActive       = false,    -- master aim active flag
    CurrentTarget   = nil,      -- current locked Player
    EnemiesInRange  = {},       -- cache of enemies in 150 stud
    HPBillboards    = {},       -- {[Player] = {billboard, label}}
    Minimized       = false,
    GUIDragging     = false,
    MiniDragging    = false,
    DragStart       = nil,
    DragFrameStart  = nil,
}

-- ═══════════════════════════════════════════════════════════
-- UTILITY: PLAYER / CHARACTER HELPERS
-- ═══════════════════════════════════════════════════════════

---Returns true if the player is alive (has character + humanoid with HP > 0)
local function IsAlive(player)
    if not player then return false end
    local char = player.Character
    if not char then return false end
    local hum = char:FindFirstChildOfClass("Humanoid")
    return hum ~= nil and hum.Health > 0
end

---Returns true if player is on the local player's team
local function IsTeammate(player)
    if not Config.AimAssist.TeamCheck then return false end
    if LocalPlayer.Team == nil or player.Team == nil then return false end
    return player.Team == LocalPlayer.Team
end

---Returns true if a player can receive damage (no ForceField, not invincible)
local function CanTakeDamage(player)
    if not Config.AimAssist.NoDmgCheck then return true end
    local char = player.Character
    if not char then return false end
    -- ForceField check
    if char:FindFirstChildOfClass("ForceField") then return false end
    -- Custom Invincible attribute
    local hum = char:FindFirstChildOfClass("Humanoid")
    if not hum then return false end
    if hum:GetAttribute("Invincible") == true then return false end
    if hum:GetAttribute("God") == true then return false end
    return true
end

---Returns the target BasePart for the given player, by configured TargetPart name
local function GetTargetPart(player, partOverride)
    local char = player.Character
    if not char then return nil end
    local name = partOverride or Config.AimAssist.TargetPart
    if name == "Head" then
        return char:FindFirstChild("Head")
    elseif name == "Torso" then
        return char:FindFirstChild("UpperTorso")
            or char:FindFirstChild("Torso")
            or char:FindFirstChild("HumanoidRootPart")
    elseif name == "HumanoidRootPart" then
        return char:FindFirstChild("HumanoidRootPart")
    end
    return char:FindFirstChild(name)
end

---Returns world distance between local player and target player
local function GetWorldDistance(player)
    local lChar = LocalPlayer.Character
    if not lChar then return math.huge end
    local lRoot = lChar:FindFirstChild("HumanoidRootPart")
    if not lRoot then return math.huge end
    local tChar = player.Character
    if not tChar then return math.huge end
    local tRoot = tChar:FindFirstChild("HumanoidRootPart")
    if not tRoot then return math.huge end
    return (lRoot.Position - tRoot.Position).Magnitude
end

---Returns screen distance of a world position from screen center
---Also returns whether it is on-screen and the raw Vector3 screenPos
local function GetScreenDistance(worldPos)
    local screenPos, onScreen = Camera:WorldToViewportPoint(worldPos)
    local center = Vector2.new(Camera.ViewportSize.X * 0.5, Camera.ViewportSize.Y * 0.5)
    local dist = (Vector2.new(screenPos.X, screenPos.Y) - center).Magnitude
    return dist, onScreen, screenPos
end

---Returns humanoid HP percentage for a player
local function GetHPPercent(player)
    local char = player.Character
    if not char then return 0 end
    local hum = char:FindFirstChildOfClass("Humanoid")
    if not hum or hum.MaxHealth == 0 then return 0 end
    return hum.Health / hum.MaxHealth
end

-- ═══════════════════════════════════════════════════════════
-- ENEMY SCAN
-- ═══════════════════════════════════════════════════════════

---Scan all players and return table of valid enemies in MaxDistance range
---Each entry: {player, distance, screenDist, onScreen, hpPct}
local function ScanEnemies()
    local results = {}
    for _, player in ipairs(Players:GetPlayers()) do
        if player == LocalPlayer then continue end
        if not IsAlive(player) then continue end
        if IsTeammate(player) then continue end
        if not CanTakeDamage(player) then continue end

        local dist = GetWorldDistance(player)
        if dist > Config.AimAssist.MaxDistance then continue end

        local part = GetTargetPart(player)
        local screenDist, onScreen = 0, false
        if part then
            screenDist, onScreen = GetScreenDistance(part.Position)
        end

        local hpPct = GetHPPercent(player)

        table.insert(results, {
            player     = player,
            distance   = dist,
            screenDist = screenDist,
            onScreen   = onScreen,
            hpPct      = hpPct,
        })
    end
    return results
end

---Pick the best target from the scan based on configured Priority
local function PickBestTarget(enemies)
    if #enemies == 0 then return nil end

    local priority = Config.AimAssist.Priority

    if priority == "Nearest" then
        table.sort(enemies, function(a, b)
            -- Weight: screen distance matters more at close range
            local wa = a.screenDist + a.distance * 0.3
            local wb = b.screenDist + b.distance * 0.3
            return wa < wb
        end)
    elseif priority == "LowestHP" then
        table.sort(enemies, function(a, b)
            return a.hpPct < b.hpPct
        end)
    elseif priority == "OnScreen" then
        -- On-screen enemies first, then by screen distance
        table.sort(enemies, function(a, b)
            if a.onScreen ~= b.onScreen then
                return a.onScreen
            end
            return a.screenDist < b.screenDist
        end)
    end

    return enemies[1].player
end

-- ═══════════════════════════════════════════════════════════
-- AIM ASSIST CORE  (runs at Camera.Value + 1 each frame)
-- ═══════════════════════════════════════════════════════════

---Directly manipulate Camera.CFrame to snap/smooth toward the target part.
---No delay: Lerp factor (1 - smoothness) means smoothness=0.04 ≈ 96% of the
---gap is closed per frame, producing near-instant lock with micro smoothing.
local function ApplyAimAssist()
    if not Config.AimAssist.Enabled then return end
    if not State.AimActive then return end

    -- Validate current target each frame
    if State.CurrentTarget then
        local valid = IsAlive(State.CurrentTarget)
            and CanTakeDamage(State.CurrentTarget)
            and GetWorldDistance(State.CurrentTarget) <= Config.AimAssist.MaxDistance
        if not valid then
            State.CurrentTarget = nil
        end
    end

    -- Try to acquire / reacquire
    if not State.CurrentTarget then
        if Config.AimAssist.AutoReacquire then
            local enemies = ScanEnemies()
            State.CurrentTarget = PickBestTarget(enemies)
        end
        if not State.CurrentTarget then return end
    end

    local part = GetTargetPart(State.CurrentTarget)
    if not part then return end

    local targetWorldPos = part.Position
    local camCF = Camera.CFrame

    -- Build the CFrame that looks at the target from current camera position
    local desiredCF = CFrame.lookAt(camCF.Position, targetWorldPos)

    -- Apply with smoothness: 0 = instant lock, 1 = no movement
    -- We use (1 - smoothness) so lower smoothness = faster
    Camera.CFrame = camCF:Lerp(desiredCF, 1 - Config.AimAssist.Smoothness)
end

-- ═══════════════════════════════════════════════════════════
-- OFF AFTER KILL SYSTEM
-- ═══════════════════════════════════════════════════════════
--[[
    Logic (runs every frame):
    1. Scan enemies in 150 studs.
    2. If enemies found AND AimAssist.Enabled:
         - Ensure State.AimActive = true
         - Reacquire target if current is dead/gone
    3. If NO enemies found:
         - Set State.AimActive = false
         - Clear target
    This means: OffAfterKill simply gates whether the zero-enemy
    condition turns off aim. If disabled, AimActive is just driven
    by the toggle. If enabled, it toggles reactively.
]]
local function OffAfterKillUpdate()
    if not Config.AimAssist.Enabled then return end

    local enemies = ScanEnemies()
    State.EnemiesInRange = enemies

    if Config.AimAssist.OffAfterKill then
        if #enemies == 0 then
            -- No enemies — turn aim off
            if State.AimActive then
                State.AimActive = false
                State.CurrentTarget = nil
            end
        else
            -- Enemies present — ensure aim is on
            if not State.AimActive then
                State.AimActive = true
            end
            -- Reacquire if needed
            if not State.CurrentTarget or not IsAlive(State.CurrentTarget) then
                State.CurrentTarget = PickBestTarget(enemies)
            end
        end
    else
        -- Not using OffAfterKill — just keep AimActive in sync with toggle
        State.AimActive = Config.AimAssist.Enabled
        if State.AimActive and (not State.CurrentTarget or not IsAlive(State.CurrentTarget)) then
            State.CurrentTarget = PickBestTarget(enemies)
        end
    end
end

-- ═══════════════════════════════════════════════════════════
-- SHOW HP SYSTEM
-- ═══════════════════════════════════════════════════════════

---Color-code HP label based on percentage
local function HPColor(pct)
    if pct > 0.65 then
        return Color3.fromRGB(80, 255, 80)
    elseif pct > 0.35 then
        return Color3.fromRGB(255, 210, 0)
    else
        return Color3.fromRGB(255, 60, 60)
    end
end

---Create or update HP BillboardGui above each visible enemy
local function UpdateHPDisplays()
    if not Config.ShowHP.Enabled then
        -- Destroy all existing
        for player, data in pairs(State.HPBillboards) do
            if data.billboard and data.billboard.Parent then
                data.billboard:Destroy()
            end
            State.HPBillboards[player] = nil
        end
        return
    end

    -- Remove stale (dead / left game)
    for player, data in pairs(State.HPBillboards) do
        if not player or not player.Parent then
            if data.billboard and data.billboard.Parent then
                data.billboard:Destroy()
            end
            State.HPBillboards[player] = nil
        end
    end

    -- Update / create for all valid enemies
    for _, player in ipairs(Players:GetPlayers()) do
        if player == LocalPlayer then continue end
        if IsTeammate(player) then continue end
        if not IsAlive(player) then
            -- Destroy billboard if they die
            if State.HPBillboards[player] then
                if State.HPBillboards[player].billboard.Parent then
                    State.HPBillboards[player].billboard:Destroy()
                end
                State.HPBillboards[player] = nil
            end
            continue
        end

        local char = player.Character
        if not char then continue end
        local head = char:FindFirstChild("Head")
        local hum  = char:FindFirstChildOfClass("Humanoid")
        if not head or not hum then continue end

        -- Create billboard if missing
        if not State.HPBillboards[player] then
            local bb = Instance.new("BillboardGui")
            bb.Name         = "AimAssistHP_" .. player.Name
            bb.Size         = UDim2.new(5, 0, 1.2, 0)
            bb.StudsOffset  = Config.ShowHP.StudsOffset
            bb.AlwaysOnTop  = Config.ShowHP.AlwaysOnTop
            bb.Adornee      = head
            bb.ResetOnSpawn = false
            bb.Parent       = head

            -- Background bar (HP bar)
            local barBg = Instance.new("Frame")
            barBg.Name = "BarBg"
            barBg.Size = UDim2.new(1, 0, 0, 6)
            barBg.Position = UDim2.new(0, 0, 1, 2)
            barBg.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
            barBg.BorderSizePixel = 0
            barBg.Parent = bb
            local bbCorner = Instance.new("UICorner")
            bbCorner.CornerRadius = UDim.new(1, 0)
            bbCorner.Parent = barBg

            local barFill = Instance.new("Frame")
            barFill.Name = "BarFill"
            barFill.Size = UDim2.new(1, 0, 1, 0)
            barFill.BackgroundColor3 = Color3.fromRGB(80, 255, 80)
            barFill.BorderSizePixel = 0
            barFill.Parent = barBg
            local bfCorner = Instance.new("UICorner")
            bfCorner.CornerRadius = UDim.new(1, 0)
            bfCorner.Parent = barFill

            -- HP text label
            local lbl = Instance.new("TextLabel")
            lbl.Name = "HPLabel"
            lbl.Size = UDim2.new(1, 0, 1, 0)
            lbl.Position = UDim2.new(0, 0, 0, 0)
            lbl.BackgroundTransparency = 1
            lbl.TextColor3 = Color3.fromRGB(255, 255, 255)
            lbl.TextStrokeTransparency = 0
            lbl.TextStrokeColor3 = Color3.fromRGB(0, 0, 0)
            lbl.Font = Enum.Font.GothamBold
            lbl.TextSize = Config.ShowHP.TextSize
            lbl.Text = "HP"
            lbl.Parent = bb

            -- Name label (smaller)
            local nameLbl = Instance.new("TextLabel")
            nameLbl.Name = "NameLabel"
            nameLbl.Size = UDim2.new(1, 0, 0, 14)
            nameLbl.Position = UDim2.new(0, 0, 1, 10)
            nameLbl.BackgroundTransparency = 1
            nameLbl.TextColor3 = Color3.fromRGB(200, 200, 255)
            nameLbl.TextStrokeTransparency = 0
            nameLbl.TextStrokeColor3 = Color3.fromRGB(0, 0, 0)
            nameLbl.Font = Enum.Font.Gotham
            nameLbl.TextSize = 12
            nameLbl.Text = player.Name
            nameLbl.Parent = bb

            State.HPBillboards[player] = {
                billboard = bb,
                label     = lbl,
                barFill   = barFill,
                nameLbl   = nameLbl,
            }
        end

        -- Update values
        local data   = State.HPBillboards[player]
        local hp     = math.floor(hum.Health)
        local maxHP  = math.floor(hum.MaxHealth)
        local pct    = maxHP > 0 and (hum.Health / hum.MaxHealth) or 0
        local col    = HPColor(pct)

        data.label.Text      = string.format("❤ %d / %d", hp, maxHP)
        data.label.TextColor3 = col
        data.barFill.Size    = UDim2.new(math.clamp(pct, 0, 1), 0, 1, 0)
        data.barFill.BackgroundColor3 = col
    end
end

-- ═══════════════════════════════════════════════════════════
-- FOV CIRCLE (Drawing API or fallback frame)
-- ═══════════════════════════════════════════════════════════
local FOVDraw = nil
local useDraw = pcall(function() -- check if Drawing API available
    local t = Drawing.new("Circle")
    t:Remove()
end)

if useDraw then
    FOVDraw = Drawing.new("Circle")
    FOVDraw.Thickness   = Config.FOVCircle.Thickness
    FOVDraw.NumSides    = 80
    FOVDraw.Radius      = Config.AimAssist.FOVRadius
    FOVDraw.Filled      = false
    FOVDraw.Visible     = false
    FOVDraw.Color       = Config.FOVCircle.Color
    FOVDraw.Transparency = 1
end

local function UpdateFOVCircle()
    if not FOVDraw then return end
    local show = Config.FOVCircle.Visible and Config.AimAssist.Enabled
    FOVDraw.Visible  = show
    FOVDraw.Radius   = Config.AimAssist.FOVRadius
    FOVDraw.Position = Vector2.new(
        Camera.ViewportSize.X * 0.5,
        Camera.ViewportSize.Y * 0.5
    )
end

-- ═══════════════════════════════════════════════════════════
-- STATUS TEXT HELPER
-- ═══════════════════════════════════════════════════════════
local StatusLabel  -- assigned after GUI build

local function RefreshStatusText()
    if not StatusLabel then return end
    local enemyCount = #State.EnemiesInRange
    local targetName = (State.CurrentTarget and State.CurrentTarget.Name) or "None"

    if not Config.AimAssist.Enabled then
        StatusLabel.Text      = "  ○  AIM OFF  |  Enemies: " .. enemyCount
        StatusLabel.TextColor3 = Color3.fromRGB(120, 120, 130)
    elseif State.AimActive then
        StatusLabel.Text      = "  ●  LOCKED: " .. targetName .. "  |  " .. enemyCount .. " enemy"
        StatusLabel.TextColor3 = Color3.fromRGB(80, 255, 120)
    else
        StatusLabel.Text      = "  ◌  STANDBY  |  No enemies in 150 stud"
        StatusLabel.TextColor3 = Color3.fromRGB(255, 200, 50)
    end
end

-- ═══════════════════════════════════════════════════════════
-- GUI CONSTRUCTION
-- ═══════════════════════════════════════════════════════════

local SG = Instance.new("ScreenGui")
SG.Name            = "AimAssistProGUI"
SG.ResetOnSpawn    = false
SG.ZIndexBehavior  = Enum.ZIndexBehavior.Global
SG.DisplayOrder    = 999
SG.Parent          = LocalPlayer:WaitForChild("PlayerGui")

local C = Config.GUI  -- shorthand

-- ────────────────────── MAIN FRAME ───────────────────────
local MainFrame = Instance.new("Frame")
MainFrame.Name              = "MainFrame"
MainFrame.Size              = UDim2.new(0, C.Width, 0, C.Height)
MainFrame.Position          = UDim2.new(0.5, -(C.Width/2), 0.5, -(C.Height/2))
MainFrame.BackgroundColor3  = C.BgColor
MainFrame.BorderSizePixel   = 0
MainFrame.ClipsDescendants  = false
MainFrame.ZIndex            = 10
MainFrame.Parent            = SG
Instance.new("UICorner", MainFrame).CornerRadius = UDim.new(0, 14)

-- Outer glow border
local GlowBorder = Instance.new("Frame")
GlowBorder.Size                = UDim2.new(1, 4, 1, 4)
GlowBorder.Position            = UDim2.new(0, -2, 0, -2)
GlowBorder.BackgroundColor3    = C.AccentColor
GlowBorder.BackgroundTransparency = 0.5
GlowBorder.BorderSizePixel     = 0
GlowBorder.ZIndex              = 9
GlowBorder.Parent              = MainFrame
Instance.new("UICorner", GlowBorder).CornerRadius = UDim.new(0, 16)

-- ────────────────────── TITLE BAR ───────────────────────
local TitleBar = Instance.new("Frame")
TitleBar.Name              = "TitleBar"
TitleBar.Size              = UDim2.new(1, 0, 0, 44)
TitleBar.BackgroundColor3  = C.AccentColor
TitleBar.BorderSizePixel   = 0
TitleBar.ZIndex            = 11
TitleBar.Parent            = MainFrame

local TitleCorner = Instance.new("UICorner")
TitleCorner.CornerRadius = UDim.new(0, 14)
TitleCorner.Parent       = TitleBar
-- Cover bottom corners of title bar
local TitleFix = Instance.new("Frame")
TitleFix.Size             = UDim2.new(1, 0, 0.5, 0)
TitleFix.Position         = UDim2.new(0, 0, 0.5, 0)
TitleFix.BackgroundColor3 = C.AccentColor
TitleFix.BorderSizePixel  = 0
TitleFix.ZIndex           = 11
TitleFix.Parent           = TitleBar

local TitleIcon = Instance.new("TextLabel")
TitleIcon.Text             = "⚡"
TitleIcon.Size             = UDim2.new(0, 36, 0, 36)
TitleIcon.Position         = UDim2.new(0, 8, 0.5, -18)
TitleIcon.BackgroundTransparency = 1
TitleIcon.TextColor3       = Color3.fromRGB(255, 255, 255)
TitleIcon.Font             = Enum.Font.GothamBold
TitleIcon.TextSize         = 20
TitleIcon.ZIndex           = 12
TitleIcon.Parent           = TitleBar

local TitleLabel = Instance.new("TextLabel")
TitleLabel.Text            = "AIM ASSIST PRO"
TitleLabel.Size            = UDim2.new(1, -130, 1, 0)
TitleLabel.Position        = UDim2.new(0, 46, 0, 0)
TitleLabel.BackgroundTransparency = 1
TitleLabel.TextColor3      = Color3.fromRGB(255, 255, 255)
TitleLabel.Font            = Enum.Font.GothamBold
TitleLabel.TextSize        = 15
TitleLabel.TextXAlignment  = Enum.TextXAlignment.Left
TitleLabel.ZIndex          = 12
TitleLabel.Parent          = TitleBar

-- Minimize button
local BtnMinimize = Instance.new("TextButton")
BtnMinimize.Name           = "BtnMinimize"
BtnMinimize.Size           = UDim2.new(0, 28, 0, 28)
BtnMinimize.Position       = UDim2.new(1, -66, 0.5, -14)
BtnMinimize.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
BtnMinimize.BackgroundTransparency = 0.7
BtnMinimize.BorderSizePixel = 0
BtnMinimize.Text           = "—"
BtnMinimize.TextColor3     = Color3.fromRGB(255, 255, 255)
BtnMinimize.Font           = Enum.Font.GothamBold
BtnMinimize.TextSize       = 13
BtnMinimize.ZIndex         = 13
BtnMinimize.Parent         = TitleBar
Instance.new("UICorner", BtnMinimize).CornerRadius = UDim.new(1, 0)

-- Close / hide button
local BtnClose = Instance.new("TextButton")
BtnClose.Name              = "BtnClose"
BtnClose.Size              = UDim2.new(0, 28, 0, 28)
BtnClose.Position          = UDim2.new(1, -32, 0.5, -14)
BtnClose.BackgroundColor3  = Color3.fromRGB(220, 60, 60)
BtnClose.BorderSizePixel   = 0
BtnClose.Text              = "✕"
BtnClose.TextColor3        = Color3.fromRGB(255, 255, 255)
BtnClose.Font              = Enum.Font.GothamBold
BtnClose.TextSize          = 12
BtnClose.ZIndex            = 13
BtnClose.Parent            = TitleBar
Instance.new("UICorner", BtnClose).CornerRadius = UDim.new(1, 0)

-- ────────────────────── SCROLL CONTENT ───────────────────────
local ScrollFrame = Instance.new("ScrollingFrame")
ScrollFrame.Name              = "ScrollFrame"
ScrollFrame.Size              = UDim2.new(1, -16, 1, -60)
ScrollFrame.Position          = UDim2.new(0, 8, 0, 52)
ScrollFrame.BackgroundTransparency = 1
ScrollFrame.BorderSizePixel   = 0
ScrollFrame.ScrollBarThickness = 3
ScrollFrame.ScrollBarImageColor3 = C.AccentColor
ScrollFrame.CanvasSize        = UDim2.new(0, 0, 0, 0)
ScrollFrame.ZIndex            = 11
ScrollFrame.Parent            = MainFrame

local ListLayout = Instance.new("UIListLayout")
ListLayout.Padding    = UDim.new(0, 6)
ListLayout.SortOrder  = Enum.SortOrder.LayoutOrder
ListLayout.Parent     = ScrollFrame

local ListPad = Instance.new("UIPadding")
ListPad.PaddingTop    = UDim.new(0, 4)
ListPad.PaddingBottom = UDim.new(0, 8)
ListPad.PaddingLeft   = UDim.new(0, 2)
ListPad.PaddingRight  = UDim.new(0, 2)
ListPad.Parent        = ScrollFrame

-- Auto-resize canvas
ListLayout:GetPropertyChangedSignal("AbsoluteContentSize"):Connect(function()
    ScrollFrame.CanvasSize = UDim2.new(0, 0, 0, ListLayout.AbsoluteContentSize.Y + 12)
end)

-- ════════════════════════════════════════════════════════════
-- GUI COMPONENT BUILDERS
-- ════════════════════════════════════════════════════════════

local function MakeSection(title, layoutOrder)
    local f = Instance.new("Frame")
    f.Size              = UDim2.new(1, 0, 0, 24)
    f.BackgroundTransparency = 1
    f.LayoutOrder       = layoutOrder
    f.Parent            = ScrollFrame

    local line = Instance.new("Frame")
    line.Size            = UDim2.new(0.3, 0, 0, 1)
    line.Position        = UDim2.new(0, 0, 0.5, 0)
    line.BackgroundColor3 = C.AccentColor
    line.BackgroundTransparency = 0.4
    line.BorderSizePixel = 0
    line.Parent          = f

    local lbl = Instance.new("TextLabel")
    lbl.Text             = "  " .. title .. "  "
    lbl.Size             = UDim2.new(0, 0, 1, 0)
    lbl.AutomaticSize    = Enum.AutomaticSize.X
    lbl.Position         = UDim2.new(0, 0, 0, 0)
    lbl.BackgroundTransparency = 1
    lbl.TextColor3       = C.AccentColor
    lbl.Font             = Enum.Font.GothamBold
    lbl.TextSize         = 11
    lbl.Parent           = f

    local line2 = Instance.new("Frame")
    line2.Size            = UDim2.new(0.3, 0, 0, 1)
    line2.Position        = UDim2.new(0.7, 0, 0.5, 0)
    line2.BackgroundColor3 = C.AccentColor
    line2.BackgroundTransparency = 0.4
    line2.BorderSizePixel = 0
    line2.Parent          = f

    return f
end

local function MakeToggle(text, configTbl, configKey, layoutOrder, callback)
    local container = Instance.new("Frame")
    container.Size              = UDim2.new(1, 0, 0, 38)
    container.BackgroundColor3  = C.PanelColor
    container.BorderSizePixel   = 0
    container.LayoutOrder       = layoutOrder
    container.Parent            = ScrollFrame
    Instance.new("UICorner", container).CornerRadius = UDim.new(0, 9)

    local lbl = Instance.new("TextLabel")
    lbl.Text             = text
    lbl.Size             = UDim2.new(1, -70, 1, 0)
    lbl.Position         = UDim2.new(0, 12, 0, 0)
    lbl.BackgroundTransparency = 1
    lbl.TextColor3       = C.TextColor
    lbl.Font             = Enum.Font.Gotham
    lbl.TextSize         = 12
    lbl.TextXAlignment   = Enum.TextXAlignment.Left
    lbl.Parent           = container

    local trackBg = Instance.new("Frame")
    trackBg.Size             = UDim2.new(0, 46, 0, 24)
    trackBg.Position         = UDim2.new(1, -58, 0.5, -12)
    trackBg.BackgroundColor3 = configTbl[configKey]
        and Color3.fromRGB(50, 185, 110)
        or Color3.fromRGB(55, 55, 70)
    trackBg.BorderSizePixel  = 0
    trackBg.Parent           = container
    Instance.new("UICorner", trackBg).CornerRadius = UDim.new(1, 0)

    local knob = Instance.new("Frame")
    knob.Size             = UDim2.new(0, 18, 0, 18)
    knob.Position         = configTbl[configKey]
        and UDim2.new(1, -21, 0.5, -9)
        or UDim2.new(0, 3, 0.5, -9)
    knob.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
    knob.BorderSizePixel  = 0
    knob.Parent           = trackBg
    Instance.new("UICorner", knob).CornerRadius = UDim.new(1, 0)

    -- Invisible click button over whole row
    local clickArea = Instance.new("TextButton")
    clickArea.Size              = UDim2.new(1, 0, 1, 0)
    clickArea.BackgroundTransparency = 1
    clickArea.Text              = ""
    clickArea.ZIndex            = container.ZIndex + 1
    clickArea.Parent            = container

    local tweenInfo = TweenInfo.new(0.15, Enum.EasingStyle.Quad)

    clickArea.MouseButton1Click:Connect(function()
        configTbl[configKey] = not configTbl[configKey]
        local val = configTbl[configKey]
        TweenService:Create(trackBg, tweenInfo, {
            BackgroundColor3 = val
                and Color3.fromRGB(50, 185, 110)
                or  Color3.fromRGB(55, 55, 70)
        }):Play()
        TweenService:Create(knob, tweenInfo, {
            Position = val
                and UDim2.new(1, -21, 0.5, -9)
                or  UDim2.new(0, 3, 0.5, -9)
        }):Play()
        if callback then callback(val) end
    end)

    return container
end

local function MakeDropdown(text, options, default, layoutOrder, callback)
    local container = Instance.new("Frame")
    container.Size             = UDim2.new(1, 0, 0, 38)
    container.BackgroundColor3 = C.PanelColor
    container.BorderSizePixel  = 0
    container.LayoutOrder      = layoutOrder
    container.ClipsDescendants = false
    container.ZIndex           = 15
    container.Parent           = ScrollFrame
    Instance.new("UICorner", container).CornerRadius = UDim.new(0, 9)

    local lbl = Instance.new("TextLabel")
    lbl.Text           = text
    lbl.Size           = UDim2.new(0.5, 0, 1, 0)
    lbl.Position       = UDim2.new(0, 12, 0, 0)
    lbl.BackgroundTransparency = 1
    lbl.TextColor3     = C.TextColor
    lbl.Font           = Enum.Font.Gotham
    lbl.TextSize       = 12
    lbl.TextXAlignment = Enum.TextXAlignment.Left
    lbl.ZIndex         = 16
    lbl.Parent         = container

    local valBtn = Instance.new("TextButton")
    valBtn.Size            = UDim2.new(0, 130, 0, 28)
    valBtn.Position        = UDim2.new(1, -140, 0.5, -14)
    valBtn.BackgroundColor3 = Color3.fromRGB(38, 38, 55)
    valBtn.BorderSizePixel = 0
    valBtn.Text            = default .. "  ▼"
    valBtn.TextColor3      = C.AccentColor
    valBtn.Font            = Enum.Font.GothamBold
    valBtn.TextSize        = 11
    valBtn.ZIndex          = 16
    valBtn.Parent          = container
    Instance.new("UICorner", valBtn).CornerRadius = UDim.new(0, 7)

    local menu    = nil
    local isOpen  = false

    valBtn.MouseButton1Click:Connect(function()
        if isOpen then
            if menu then menu:Destroy(); menu = nil end
            isOpen = false
            return
        end
        isOpen = true
        menu = Instance.new("Frame")
        menu.Size             = UDim2.new(0, 130, 0, #options * 30 + 6)
        menu.Position         = UDim2.new(1, -140, 1, 4)
        menu.BackgroundColor3 = Color3.fromRGB(28, 28, 42)
        menu.BorderSizePixel  = 0
        menu.ZIndex           = 30
        menu.Parent           = container
        Instance.new("UICorner", menu).CornerRadius = UDim.new(0, 8)

        local mLayout = Instance.new("UIListLayout")
        mLayout.Padding  = UDim.new(0, 2)
        mLayout.Parent   = menu
        local mPad = Instance.new("UIPadding")
        mPad.PaddingTop  = UDim.new(0, 3)
        mPad.PaddingLeft  = UDim.new(0, 3)
        mPad.PaddingRight = UDim.new(0, 3)
        mPad.Parent      = menu

        for _, opt in ipairs(options) do
            local optBtn = Instance.new("TextButton")
            optBtn.Size            = UDim2.new(1, 0, 0, 28)
            optBtn.BackgroundColor3 = Color3.fromRGB(40, 40, 58)
            optBtn.BorderSizePixel = 0
            optBtn.Text            = opt
            optBtn.TextColor3      = C.TextColor
            optBtn.Font            = Enum.Font.Gotham
            optBtn.TextSize        = 11
            optBtn.ZIndex          = 31
            optBtn.Parent          = menu
            Instance.new("UICorner", optBtn).CornerRadius = UDim.new(0, 6)

            optBtn.MouseEnter:Connect(function()
                optBtn.BackgroundColor3 = C.AccentColor
            end)
            optBtn.MouseLeave:Connect(function()
                optBtn.BackgroundColor3 = Color3.fromRGB(40, 40, 58)
            end)
            optBtn.MouseButton1Click:Connect(function()
                valBtn.Text = opt .. "  ▼"
                if menu then menu:Destroy(); menu = nil end
                isOpen = false
                if callback then callback(opt) end
            end)
        end
    end)

    return container
end

local function MakeSlider(text, minV, maxV, initV, layoutOrder, fmt, callback)
    local container = Instance.new("Frame")
    container.Size             = UDim2.new(1, 0, 0, 52)
    container.BackgroundColor3 = C.PanelColor
    container.BorderSizePixel  = 0
    container.LayoutOrder      = layoutOrder
    container.Parent           = ScrollFrame
    Instance.new("UICorner", container).CornerRadius = UDim.new(0, 9)

    local lbl = Instance.new("TextLabel")
    lbl.Text           = text
    lbl.Size           = UDim2.new(0.65, 0, 0, 22)
    lbl.Position       = UDim2.new(0, 12, 0, 6)
    lbl.BackgroundTransparency = 1
    lbl.TextColor3     = C.TextColor
    lbl.Font           = Enum.Font.Gotham
    lbl.TextSize       = 12
    lbl.TextXAlignment = Enum.TextXAlignment.Left
    lbl.Parent         = container

    local valLbl = Instance.new("TextLabel")
    valLbl.Text           = string.format(fmt or "%d", initV)
    valLbl.Size           = UDim2.new(0.35, -12, 0, 22)
    valLbl.Position       = UDim2.new(0.65, 0, 0, 6)
    valLbl.BackgroundTransparency = 1
    valLbl.TextColor3     = C.AccentColor
    valLbl.Font           = Enum.Font.GothamBold
    valLbl.TextSize       = 12
    valLbl.TextXAlignment = Enum.TextXAlignment.Right
    valLbl.Parent         = container

    local track = Instance.new("Frame")
    track.Size            = UDim2.new(1, -24, 0, 6)
    track.Position        = UDim2.new(0, 12, 1, -18)
    track.BackgroundColor3 = Color3.fromRGB(40, 40, 58)
    track.BorderSizePixel = 0
    track.Parent          = container
    Instance.new("UICorner", track).CornerRadius = UDim.new(1, 0)

    local initPct = math.clamp((initV - minV) / (maxV - minV), 0, 1)

    local fill = Instance.new("Frame")
    fill.Size             = UDim2.new(initPct, 0, 1, 0)
    fill.BackgroundColor3 = C.AccentColor
    fill.BorderSizePixel  = 0
    fill.Parent           = track
    Instance.new("UICorner", fill).CornerRadius = UDim.new(1, 0)

    local knob = Instance.new("Frame")
    knob.Size             = UDim2.new(0, 14, 0, 14)
    knob.Position         = UDim2.new(initPct, -7, 0.5, -7)
    knob.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
    knob.BorderSizePixel  = 0
    knob.ZIndex           = track.ZIndex + 1
    knob.Parent           = track
    Instance.new("UICorner", knob).CornerRadius = UDim.new(1, 0)

    local isDragging = false

    local inputConn, changedConn

    local knobBtn = Instance.new("TextButton")
    knobBtn.Size               = UDim2.new(2, 0, 2, 0)
    knobBtn.Position           = UDim2.new(-0.5, 0, -0.5, 0)
    knobBtn.BackgroundTransparency = 1
    knobBtn.Text               = ""
    knobBtn.ZIndex             = knob.ZIndex + 1
    knobBtn.Parent             = knob

    knobBtn.MouseButton1Down:Connect(function()
        isDragging = true
    end)

    changedConn = UserInputService.InputChanged:Connect(function(input)
        if isDragging and input.UserInputType == Enum.UserInputType.MouseMovement then
            local mX = UserInputService:GetMouseLocation().X
            local tX = track.AbsolutePosition.X
            local tW = track.AbsoluteSize.X
            local pct = math.clamp((mX - tX) / tW, 0, 1)
            local value
            if fmt and fmt:find("%.") then
                -- float slider
                value = minV + (maxV - minV) * pct
                value = math.floor(value * 100 + 0.5) / 100
            else
                value = math.floor(minV + (maxV - minV) * pct + 0.5)
            end
            fill.Size     = UDim2.new(pct, 0, 1, 0)
            knob.Position = UDim2.new(pct, -7, 0.5, -7)
            valLbl.Text   = string.format(fmt or "%d", value)
            if callback then callback(value) end
        end
    end)

    inputConn = UserInputService.InputEnded:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 then
            isDragging = false
        end
    end)

    return container
end

local function MakeInfoRow(text, layoutOrder)
    local container = Instance.new("Frame")
    container.Size             = UDim2.new(1, 0, 0, 34)
    container.BackgroundColor3 = Color3.fromRGB(18, 18, 28)
    container.BorderSizePixel  = 0
    container.LayoutOrder      = layoutOrder
    container.Parent           = ScrollFrame
    Instance.new("UICorner", container).CornerRadius = UDim.new(0, 9)

    local lbl = Instance.new("TextLabel")
    lbl.Text           = text
    lbl.Size           = UDim2.new(1, -16, 1, 0)
    lbl.Position       = UDim2.new(0, 12, 0, 0)
    lbl.BackgroundTransparency = 1
    lbl.TextColor3     = Color3.fromRGB(160, 160, 180)
    lbl.Font           = Enum.Font.Gotham
    lbl.TextSize       = 11
    lbl.TextXAlignment = Enum.TextXAlignment.Left
    lbl.TextWrapped    = true
    lbl.Parent         = container

    StatusLabel = lbl  -- overwritten by the last call to MakeInfoRow for status
    return container, lbl
end

-- ════════════════════════════════════════════════════════════
-- POPULATE GUI CONTENT
-- ════════════════════════════════════════════════════════════

MakeSection("AIM ASSIST", 1)

MakeToggle("Enable Aim Assist", Config.AimAssist, "Enabled", 2, function(val)
    State.AimActive = val
    if val then
        -- Immediately scan and lock
        local enemies = ScanEnemies()
        State.CurrentTarget = PickBestTarget(enemies)
    else
        State.CurrentTarget = nil
    end
end)

MakeToggle("Team Check  (skip allies)", Config.AimAssist, "TeamCheck", 3, nil)
MakeToggle("No-Damage Skip  (ForceField / Invincible)", Config.AimAssist, "NoDmgCheck", 4, nil)
MakeToggle("Off After Kill  (auto-off when 0 enemies in 150 stud)", Config.AimAssist, "OffAfterKill", 5, nil)
MakeToggle("Auto Reacquire  (lock new enemy instantly)", Config.AimAssist, "AutoReacquire", 6, nil)

MakeSection("TARGET SETTINGS", 10)

MakeDropdown("Aim Part", {"Head", "Torso", "HumanoidRootPart"}, "Head", 11, function(val)
    Config.AimAssist.TargetPart = val
end)

MakeDropdown("Priority", {"Nearest", "LowestHP", "OnScreen"}, "Nearest", 12, function(val)
    Config.AimAssist.Priority = val
end)

MakeSlider("Max Distance  (studs)", 20, 500, 150, 13, "%d", function(val)
    Config.AimAssist.MaxDistance = val
end)

MakeSlider("Smoothness  (lower = faster)", 1, 50, 4, 14, "%.2f", function(val)
    Config.AimAssist.Smoothness = val / 100
end)

MakeSlider("FOV Radius  (px)", 50, 500, 250, 15, "%d", function(val)
    Config.AimAssist.FOVRadius = val
end)

MakeSection("VISUALS", 20)

MakeToggle("Show HP above enemy heads", Config.ShowHP, "Enabled", 21, nil)
MakeToggle("HP always on top  (through walls)", Config.ShowHP, "AlwaysOnTop", 22, function(val)
    for _, data in pairs(State.HPBillboards) do
        if data.billboard then
            data.billboard.AlwaysOnTop = val
        end
    end
end)
MakeToggle("Show FOV Circle", Config.FOVCircle, "Visible", 23, function(val)
    if FOVDraw then FOVDraw.Visible = val and Config.AimAssist.Enabled end
end)

MakeSection("STATUS", 30)

local _, StatusLbl = MakeInfoRow("  ○  AIM OFF  |  Enemies: 0", 31)
StatusLabel = StatusLbl

-- ════════════════════════════════════════════════════════════
-- MINIMIZED CIRCLE BUTTON
-- ════════════════════════════════════════════════════════════

local MiniCircle = Instance.new("TextButton")
MiniCircle.Name              = "MiniCircle"
MiniCircle.Size              = UDim2.new(0, 60, 0, 60)
MiniCircle.Position          = MainFrame.Position
MiniCircle.BackgroundColor3  = C.AccentColor
MiniCircle.BorderSizePixel   = 0
MiniCircle.Text              = "⚡"
MiniCircle.TextColor3        = Color3.fromRGB(255, 255, 255)
MiniCircle.Font              = Enum.Font.GothamBold
MiniCircle.TextSize          = 24
MiniCircle.Visible           = false
MiniCircle.ZIndex            = 20
MiniCircle.Parent            = SG
Instance.new("UICorner", MiniCircle).CornerRadius = UDim.new(1, 0)

-- Pulsing ring around circle to show aim status
local MiniRing = Instance.new("Frame")
MiniRing.Name             = "MiniRing"
MiniRing.Size             = UDim2.new(1, 10, 1, 10)
MiniRing.Position         = UDim2.new(0, -5, 0, -5)
MiniRing.BackgroundColor3 = Color3.fromRGB(80, 80, 80)
MiniRing.BackgroundTransparency = 0.5
MiniRing.BorderSizePixel  = 0
MiniRing.ZIndex           = 19
MiniRing.Parent           = MiniCircle
Instance.new("UICorner", MiniRing).CornerRadius = UDim.new(1, 0)

-- ════════════════════════════════════════════════════════════
-- DRAG LOGIC  (Main Frame via TitleBar)
-- ════════════════════════════════════════════════════════════

do
    local dragData = {active = false, start = nil, frameStart = nil}

    TitleBar.InputBegan:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 then
            dragData.active     = true
            dragData.start      = input.Position
            dragData.frameStart = MainFrame.Position
        end
    end)

    TitleBar.InputEnded:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 then
            dragData.active = false
        end
    end)

    UserInputService.InputChanged:Connect(function(input)
        if dragData.active and input.UserInputType == Enum.UserInputType.MouseMovement then
            local delta = input.Position - dragData.start
            MainFrame.Position = UDim2.new(
                dragData.frameStart.X.Scale,
                dragData.frameStart.X.Offset + delta.X,
                dragData.frameStart.Y.Scale,
                dragData.frameStart.Y.Offset + delta.Y
            )
        end
    end)
end

-- ════════════════════════════════════════════════════════════
-- DRAG LOGIC  (Minimized Circle)
-- ════════════════════════════════════════════════════════════

do
    local dragData = {active = false, moved = false, start = nil, frameStart = nil}

    MiniCircle.InputBegan:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 then
            dragData.active     = true
            dragData.moved      = false
            dragData.start      = input.Position
            dragData.frameStart = MiniCircle.Position
        end
    end)

    MiniCircle.InputEnded:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 then
            dragData.active = false
        end
    end)

    UserInputService.InputChanged:Connect(function(input)
        if dragData.active and input.UserInputType == Enum.UserInputType.MouseMovement then
            local delta = input.Position - dragData.start
            if delta.Magnitude > 4 then dragData.moved = true end
            MiniCircle.Position = UDim2.new(
                dragData.frameStart.X.Scale,
                dragData.frameStart.X.Offset + delta.X,
                dragData.frameStart.Y.Scale,
                dragData.frameStart.Y.Offset + delta.Y
            )
        end
    end)

    -- Tap to expand (if not dragging)
    MiniCircle.MouseButton1Click:Connect(function()
        if not dragData.moved then
            -- Expand
            MainFrame.Position = MiniCircle.Position
            MainFrame.Visible  = true
            MiniCircle.Visible = false
            State.Minimized    = false
        end
        dragData.moved = false
    end)
end

-- ════════════════════════════════════════════════════════════
-- MINIMIZE / CLOSE
-- ════════════════════════════════════════════════════════════

local function DoMinimize()
    State.Minimized    = true
    MiniCircle.Position = MainFrame.Position
    MainFrame.Visible  = false
    MiniCircle.Visible = true
end

BtnMinimize.MouseButton1Click:Connect(DoMinimize)
BtnClose.MouseButton1Click:Connect(DoMinimize)

-- ════════════════════════════════════════════════════════════
-- STATUS RING UPDATE (mini circle ring color)
-- ════════════════════════════════════════════════════════════

local function UpdateMiniRing()
    if not State.Minimized then return end
    if Config.AimAssist.Enabled and State.AimActive then
        MiniRing.BackgroundColor3 = Color3.fromRGB(60, 220, 100)
    elseif Config.AimAssist.Enabled then
        MiniRing.BackgroundColor3 = Color3.fromRGB(255, 200, 50)
    else
        MiniRing.BackgroundColor3 = Color3.fromRGB(80, 80, 80)
    end
end

-- ════════════════════════════════════════════════════════════
-- MAIN RENDER LOOP
-- Uses BindToRenderStep at Camera.Value + 1 to run AFTER camera
-- movement but still in the same frame, ensuring no visible delay.
-- ════════════════════════════════════════════════════════════

RunService:BindToRenderStep(
    "AimAssistPro_Core",
    Enum.RenderPriority.Camera.Value + 1,
    function(dt)

        -- ① Off-After-Kill / enemy scan (every frame)
        OffAfterKillUpdate()

        -- ② Apply aim assist
        ApplyAimAssist()

        -- ③ FOV circle
        UpdateFOVCircle()

        -- ④ HP displays
        UpdateHPDisplays()

        -- ⑤ Status text
        RefreshStatusText()

        -- ⑥ Mini ring
        UpdateMiniRing()
    end
)

-- ════════════════════════════════════════════════════════════
-- CLEANUP
-- ════════════════════════════════════════════════════════════

SG.AncestryChanged:Connect(function(_, parent)
    if not parent then
        RunService:UnbindFromRenderStep("AimAssistPro_Core")
        if FOVDraw then
            pcall(function() FOVDraw:Remove() end)
        end
        for player, data in pairs(State.HPBillboards) do
            if data.billboard and data.billboard.Parent then
                data.billboard:Destroy()
            end
        end
    end
end)

-- ════════════════════════════════════════════════════════════
-- CONSOLE STARTUP MESSAGE
-- ════════════════════════════════════════════════════════════

print("╔══════════════════════════════════╗")
print("║   AIM ASSIST PRO  — Loaded ✓     ║")
print("║   Tap circle once to expand GUI  ║")
print("╚══════════════════════════════════╝")
