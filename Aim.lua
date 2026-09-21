-- Services
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local Workspace = game:GetService("Workspace")

local LocalPlayer = Players.LocalPlayer
local Camera = Workspace.CurrentCamera

--------------------------------------------------------------------------------
-- CONFIGURATION & STATE MANAGEMENT
--------------------------------------------------------------------------------
local Config = {
    AimEnabled = false,
    MagicBullet = true, -- MỚI: Bật/Tắt tính năng Magic Bullet
    TargetPart = "Head", -- "Head" hoặc "HumanoidRootPart"
    OffAfterKill = false,
    ShowHP = false,
    AutoLockOffDistance = 150, -- Bán kính 3D (Studs)
    TeamCheck = true,
    WallCheck = true,
    
    -- Smooth Aim & FOV Circle Config
    Smoothness = 0.5,
    UseFOV = true,
    FOVRadius = 120, -- Pixels
    FOVColor = Color3.fromRGB(0, 255, 170)
}

local CurrentTarget = nil
local ESPFolder = Instance.new("Folder")
ESPFolder.Name = "FPS_ESP_Folder"
ESPFolder.Parent = Workspace

--------------------------------------------------------------------------------
-- DRAWING API: FOV CIRCLE CREATION
--------------------------------------------------------------------------------
local FOVCircle = Drawing.new("Circle")
FOVCircle.Thickness = 1.5
FOVCircle.NumSides = 64
FOVCircle.Radius = Config.FOVRadius
FOVCircle.Filled = false
FOVCircle.Visible = Config.UseFOV
FOVCircle.Color = Config.FOVColor
FOVCircle.Transparency = 0.8

RunService.RenderStepped:Connect(function()
    local viewportSize = Camera.ViewportSize
    FOVCircle.Position = Vector2.new(viewportSize.X / 2, viewportSize.Y / 2)
    FOVCircle.Radius = Config.FOVRadius
    FOVCircle.Visible = Config.UseFOV and Config.AimEnabled
end)

--------------------------------------------------------------------------------
-- CORE AIM ASSIST & MAGIC BULLET HELPER FUNCTIONS
--------------------------------------------------------------------------------

-- Kiểm tra đồng đội
local function IsTeammate(player)
    if not Config.TeamCheck then return false end
    if player.Team ~= nil and LocalPlayer.Team ~= nil then
        return player.Team == LocalPlayer.Team
    end
    return false
end

-- Kiểm tra Wall Check
local function IsVisible(targetPart)
    if not Config.WallCheck then return true end
    
    local myChar = LocalPlayer.Character
    if not myChar then return false end
    
    local origin = Camera.CFrame.Position
    local destination = targetPart.Position
    local direction = destination - origin

    local raycastParams = RaycastParams.new()
    raycastParams.FilterType = Enum.RaycastFilterType.Exclude
    
    local ignoreList = {myChar}
    if targetPart.Parent then
        table.insert(ignoreList, targetPart.Parent)
    end
    raycastParams.FilterDescendantsInstances = ignoreList
    raycastParams.IgnoreWater = true

    local result = Workspace:Raycast(origin, direction, raycastParams)
    return result == nil
end

-- Kiểm tra mục tiêu nằm trong FOV Circle
local function IsInFOV(targetPart)
    if not Config.UseFOV then return true end
    
    local screenPos, onScreen = Camera:WorldToViewportPoint(targetPart.Position)
    if not onScreen then return false end
    
    local screenCenter = Vector2.new(Camera.ViewportSize.X / 2, Camera.ViewportSize.Y / 2)
    local targetVector = Vector2.new(screenPos.X, screenPos.Y)
    local distance = (targetVector - screenCenter).Magnitude
    
    return distance <= Config.FOVRadius
end

-- Kiểm tra hợp lệ mục tiêu
local function IsValidTarget(player)
    if player == LocalPlayer then return false end
    if IsTeammate(player) then return false end
    
    local character = player.Character
    if not character then return false end
    
    local humanoid = character:FindFirstChildOfClass("Humanoid")
    local targetPart = character:FindFirstChild(Config.TargetPart) or character:FindFirstChild("HumanoidRootPart")
    
    if not humanoid or humanoid.Health <= 0 then return false end
    if not targetPart then return false end
    
    if not IsVisible(targetPart) then return false end
    
    return true, character, humanoid, targetPart
end

-- Tìm kẻ địch gần tâm ngắm nhất
local function GetNearestEnemy()
    local myChar = LocalPlayer.Character
    if not myChar then return nil end
    local myRoot = myChar:FindFirstChild("HumanoidRootPart")
    if not myRoot then return nil end
    
    local closestEnemy = nil
    local shortestScreenDist = math.huge
    local screenCenter = Vector2.new(Camera.ViewportSize.X / 2, Camera.ViewportSize.Y / 2)

    for _, player in ipairs(Players:GetPlayers()) do
        local valid, character, humanoid, targetPart = IsValidTarget(player)
        if valid then
            local dist3D = (targetPart.Position - myRoot.Position).Magnitude
            
            if dist3D <= Config.AutoLockOffDistance then
                if IsInFOV(targetPart) then
                    local screenPos = Camera:WorldToViewportPoint(targetPart.Position)
                    local screenDist = (Vector2.new(screenPos.X, screenPos.Y) - screenCenter).Magnitude
                    
                    if screenDist < shortestScreenDist then
                        shortestScreenDist = screenDist
                        closestEnemy = {
                            Player = player,
                            Character = character,
                            Humanoid = humanoid,
                            Part = targetPart,
                            Distance = dist3D
                        }
                    end
                end
            end
        end
    end

    return closestEnemy
end

-- Đếm số lượng kẻ địch trong khoảng cách 150 studs
local function GetEnemiesIn150Studs()
    local myChar = LocalPlayer.Character
    if not myChar me.Parent then return 0 end
    local myRoot = myChar:FindFirstChild("HumanoidRootPart")
    if not myRoot then return 0 end

    local count = 0
    for _, player in ipairs(Players:GetPlayers()) do
        local valid, _, _, targetPart = IsValidTarget(player)
        if valid then
            local dist = (targetPart.Position - myRoot.Position).Magnitude
            if dist <= Config.AutoLockOffDistance then
                count = count + 1
            end
        end
    end
    return count
end

--------------------------------------------------------------------------------
-- HOOKING ENGINE FOR MAGIC BULLET (CALCULATE DIRECTION)
--------------------------------------------------------------------------------
-- Hàm trả về tọa độ hoặc hướng bắn được Magic Bullet bẻ cong sang kẻ địch
function GetMagicBulletDirection(originPosition)
    if Config.AimEnabled and Config.MagicBullet and CurrentTarget then
        local targetPos = CurrentTarget.Part.Position
        return (targetPos - originPosition).Unit
    end
    return nil
end

--------------------------------------------------------------------------------
-- HIGH-SPEED AIM BOT ENGINE
--------------------------------------------------------------------------------
local RENDER_PRIORITY = Enum.RenderPriority.Camera.Value + 1

RunService:BindToRenderStep("UltraFastAimAssistEngine", RENDER_PRIORITY, function(deltaTime)
    -- Logic Auto OFF / Auto ON dựa trên bán kính 150 studs
    if Config.OffAfterKill then
        local enemiesAround = GetEnemiesIn150Studs()
        if enemiesAround == 0 then
            if Config.AimEnabled then
                Config.AimEnabled = false
                CurrentTarget = nil
            end
        else
            if not Config.AimEnabled then
                Config.AimEnabled = true
            end
        end
    end

    -- Quét kẻ địch hiện tại
    if Config.AimEnabled then
        local targetData = GetNearestEnemy()
        if targetData then
            CurrentTarget = targetData
            
            -- Nếu tắt Magic Bullet thì mới xoay Camera trực tiếp (Camera Aim Assist)
            if not Config.MagicBullet then
                local targetPos = targetData.Part.Position
                local camPos = Camera.CFrame.Position
                local targetCFrame = CFrame.new(camPos, targetPos)
                
                Camera.CFrame = Camera.CFrame:Lerp(targetCFrame, math.clamp(Config.Smoothness, 0.01, 1))
            end
        else
            CurrentTarget = nil
        end
    end
end)

--------------------------------------------------------------------------------
-- ESP / SHOW HP SYSTEM
--------------------------------------------------------------------------------
local function CreateESP(player)
    local function ApplyESP(character)
        if not character then return end
        local head = character:WaitForChild("Head", 3)
        if not head then return end
        
        local bgui = Instance.new("BillboardGui")
        bgui.Name = "ESP_Health"
        bgui.Adornee = head
        bgui.Size = UDim2.new(0, 100, 0, 30)
        bgui.StudsOffset = Vector3.new(0, 2.5, 0)
        bgui.AlwaysOnTop = true
        
        local textLabel = Instance.new("TextLabel")
        textLabel.Size = UDim2.new(1, 0, 1, 0)
        textLabel.BackgroundTransparency = 1
        textLabel.TextColor3 = Color3.fromRGB(255, 50, 50)
        textLabel.TextStrokeTransparency = 0
        textLabel.Font = Enum.Font.SourceSansBold
        textLabel.TextSize = 14
        textLabel.Parent = bgui
        
        bgui.Parent = ESPFolder

        local humanoid = character:FindFirstChildOfClass("Humanoid")
        local renderConn
        renderConn = RunService.RenderStepped:Connect(function()
            if not character or not character.Parent or not humanoid or humanoid.Health <= 0 then
                bgui:Destroy()
                renderConn:Disconnect()
                return
            end

            if Config.ShowHP and not IsTeammate(player) and player ~= LocalPlayer then
                bgui.Enabled = true
                textLabel.Text = string.format("%s\nHP: %d/%d", player.Name, math.floor(humanoid.Health), math.floor(humanoid.MaxHealth))
            else
                bgui.Enabled = false
            end
        end)
    end

    if player.Character then ApplyESP(player.Character) end
    player.CharacterAdded:Connect(ApplyESP)
end

for _, p in ipairs(Players:GetPlayers()) do CreateESP(p) end
Players.PlayerAdded:Connect(CreateESP)

--------------------------------------------------------------------------------
-- GUI CREATION
--------------------------------------------------------------------------------
local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "FPS_AimAssist_UI"
ScreenGui.ResetOnSpawn = false
ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui")

local MainFrame = Instance.new("Frame")
MainFrame.Name = "MainFrame"
MainFrame.Size = UDim2.new(0, 240, 0, 510)
MainFrame.Position = UDim2.new(0.5, -120, 0.4, -255)
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
MainFrame.BorderSizePixel = 0
MainFrame.Active = true
MainFrame.Parent = ScreenGui

local UICorner = Instance.new("UICorner")
UICorner.CornerRadius = UDim.new(0, 12)
UICorner.Parent = MainFrame

local TitleBar = Instance.new("TextLabel")
TitleBar.Size = UDim2.new(1, -40, 0, 35)
TitleBar.Position = UDim2.new(0, 10, 0, 0)
TitleBar.Text = "FPS ASSIST PRO"
TitleBar.TextColor3 = Color3.fromRGB(255, 255, 255)
TitleBar.Font = Enum.Font.GothamBold
TitleBar.TextSize = 14
TitleBar.TextXAlignment = Enum.TextXAlignment.Left
TitleBar.BackgroundTransparency = 1
TitleBar.Parent = MainFrame

local MinimizeBtn = Instance.new("TextButton")
MinimizeBtn.Size = UDim2.new(0, 25, 0, 25)
MinimizeBtn.Position = UDim2.new(1, -30, 0, 5)
MinimizeBtn.Text = "-"
MinimizeBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
MinimizeBtn.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
MinimizeBtn.Font = Enum.Font.GothamBold
MinimizeBtn.TextSize = 16
MinimizeBtn.Parent = MainFrame

local MinCorner = Instance.new("UICorner")
MinCorner.CornerRadius = UDim.new(1, 0)
MinCorner.Parent = MinimizeBtn

local FloatCircle = Instance.new("TextButton")
FloatCircle.Name = "FloatCircle"
FloatCircle.Size = UDim2.new(0, 50, 0, 50)
FloatCircle.Position = MainFrame.Position
FloatCircle.BackgroundColor3 = Color3.fromRGB(0, 170, 255)
FloatCircle.Text = "AIM"
FloatCircle.TextColor3 = Color3.fromRGB(255, 255, 255)
FloatCircle.Font = Enum.Font.GothamBold
FloatCircle.TextSize = 12
FloatCircle.Visible = false
FloatCircle.Active = true
FloatCircle.Parent = ScreenGui

local CircleCorner = Instance.new("UICorner")
CircleCorner.CornerRadius = UDim.new(1, 0)
CircleCorner.Parent = FloatCircle

--------------------------------------------------------------------------------
-- DRAGGABLE LOGIC
--------------------------------------------------------------------------------
local function MakeDraggable(guiObject)
    local dragging, dragInput, dragStart, startPos

    guiObject.InputBegan:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then
            dragging = true
            dragStart = input.Position
            startPos = guiObject.Position

            input.Changed:Connect(function()
                if input.UserInputState == Enum.UserInputState.End then
                    dragging = false
                end
            end)
        end
    end)

    guiObject.InputChanged:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseMovement or input.UserInputType == Enum.UserInputType.Touch then
            dragInput = input
        end
    end)

    UserInputService.InputChanged:Connect(function(input)
        if input == dragInput and dragging then
            local delta = input.Position - dragStart
            guiObject.Position = UDim2.new(
                startPos.X.Scale, startPos.X.Offset + delta.X,
                startPos.Y.Scale, startPos.Y.Offset + delta.Y
            )
        end
    end)
end

MakeDraggable(MainFrame)
MakeDraggable(FloatCircle)

--------------------------------------------------------------------------------
-- UI CONTROLS BUILDER
--------------------------------------------------------------------------------
local Container = Instance.new("Frame")
Container.Size = UDim2.new(1, -20, 1, -45)
Container.Position = UDim2.new(0, 10, 0, 40)
Container.BackgroundTransparency = 1
Container.Parent = MainFrame

local UIListLayout = Instance.new("UIListLayout")
UIListLayout.SortOrder = Enum.SortOrder.LayoutOrder
UIListLayout.Padding = UDim.new(0, 8)
UIListLayout.Parent = Container

local function CreateToggleButton(text, defaultState, callback)
    local btn = Instance.new("TextButton")
    btn.Size = UDim2.new(1, 0, 0, 32)
    btn.BackgroundColor3 = defaultState and Color3.fromRGB(0, 170, 100) or Color3.fromRGB(40, 40, 50)
    btn.Text = text .. ": " .. (defaultState and "ON" or "OFF")
    btn.TextColor3 = Color3.fromRGB(255, 255, 255)
    btn.Font = Enum.Font.GothamSemibold
    btn.TextSize = 11
    btn.Parent = Container

    local btnCorner = Instance.new("UICorner")
    btnCorner.CornerRadius = UDim.new(0, 6)
    btnCorner.Parent = btn

    local state = defaultState
    btn.MouseButton1Click:Connect(function()
        state = not state
        btn.BackgroundColor3 = state and Color3.fromRGB(0, 170, 100) or Color3.fromRGB(40, 40, 50)
        btn.Text = text .. ": " .. (state and "ON" or "OFF")
        callback(state)
    end)
    return btn
end

-- 1. Aim Assist Toggle
CreateToggleButton("Aim Assist Ultra", Config.AimEnabled, function(st)
    Config.AimEnabled = st
end)

-- 2. MỚI: Magic Bullet Toggle
CreateToggleButton("Magic Bullet (Silent Aim)", Config.MagicBullet, function(st)
    Config.MagicBullet = st
end)

-- 3. Target Body Part Selector
local TargetPartBtn = Instance.new("TextButton")
TargetPartBtn.Size = UDim2.new(1, 0, 0, 32)
TargetPartBtn.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
TargetPartBtn.Text = "Target Part: HEAD"
TargetPartBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
TargetPartBtn.Font = Enum.Font.GothamSemibold
TargetPartBtn.TextSize = 11
TargetPartBtn.Parent = Container

local TPartCorner = Instance.new("UICorner")
TPartCorner.CornerRadius = UDim.new(0, 6)
TPartCorner.Parent = TargetPartBtn

TargetPartBtn.MouseButton1Click:Connect(function()
    if Config.TargetPart == "Head" then
        Config.TargetPart = "HumanoidRootPart"
        TargetPartBtn.Text = "Target Part: TORSO"
    else
        Config.TargetPart = "Head"
        TargetPartBtn.Text = "Target Part: HEAD"
    end
end)

-- 4. Smooth Aim Adjuster
local SmoothBtn = Instance.new("TextButton")
SmoothBtn.Size = UDim2.new(1, 0, 0, 32)
SmoothBtn.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
SmoothBtn.Text = "Smoothness: FAST (0.5)"
SmoothBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SmoothBtn.Font = Enum.Font.GothamSemibold
SmoothBtn.TextSize = 11
SmoothBtn.Parent = Container

local SmoothCorner = Instance.new("UICorner")
SmoothCorner.CornerRadius = UDim.new(0, 6)
SmoothCorner.Parent = SmoothBtn

local smoothStates = {
    {Name = "INSTANT (1.0)", Val = 1.0},
    {Name = "FAST (0.5)", Val = 0.5},
    {Name = "MEDIUM (0.2)", Val = 0.2},
    {Name = "SLOW/SMOOTH (0.08)", Val = 0.08}
}
local currentSmoothIdx = 2

SmoothBtn.MouseButton1Click:Connect(function()
    currentSmoothIdx = (currentSmoothIdx % #smoothStates) + 1
    Config.Smoothness = smoothStates[currentSmoothIdx].Val
    SmoothBtn.Text = "Smoothness: " .. smoothStates[currentSmoothIdx].Name
end)

-- 5. Toggle FOV Circle
CreateToggleButton("Draw FOV Circle", Config.UseFOV, function(st)
    Config.UseFOV = st
end)

-- 6. Adjust FOV Size
local FOVBtn = Instance.new("TextButton")
FOVBtn.Size = UDim2.new(1, 0, 0, 32)
FOVBtn.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
FOVBtn.Text = "FOV Size: MEDIUM (120px)"
FOVBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
FOVBtn.Font = Enum.Font.GothamSemibold
FOVBtn.TextSize = 11
FOVBtn.Parent = Container

local FOVCorner = Instance.new("UICorner")
FOVCorner.CornerRadius = UDim.new(0, 6)
FOVCorner.Parent = FOVBtn

local fovSizes = {
    {Name = "SMALL (80px)", Val = 80},
    {Name = "MEDIUM (120px)", Val = 120},
    {Name = "LARGE (200px)", Val = 200},
    {Name = "ULTRA (350px)", Val = 350}
}
local currentFovIdx = 2

FOVBtn.MouseButton1Click:Connect(function()
    currentFovIdx = (currentFovIdx % #fovSizes) + 1
    Config.FOVRadius = fovSizes[currentFovIdx].Val
    FOVBtn.Text = "FOV Size: " .. fovSizes[currentFovIdx].Name
end)

-- 7. Wall Check Toggle
CreateToggleButton("Wall Check (Visible Only)", Config.WallCheck, function(st)
    Config.WallCheck = st
end)

-- 8. Off After Kill Toggle
CreateToggleButton("Off/Auto-On (150 Studs)", Config.OffAfterKill, function(st)
    Config.OffAfterKill = st
end)

-- 9. Show HP Toggle
CreateToggleButton("Show HP (ESP)", Config.ShowHP, function(st)
    Config.ShowHP = st
end)

-- 10. Team Check Toggle
CreateToggleButton("Team Check", Config.TeamCheck, function(st)
    Config.TeamCheck = st
end)

--------------------------------------------------------------------------------
-- MINIMIZE / FLOATING TOGGLE EVENT
--------------------------------------------------------------------------------
MinimizeBtn.MouseButton1Click:Connect(function()
    MainFrame.Visible = false
    FloatCircle.Position = MainFrame.Position
    FloatCircle.Visible = true
end)

FloatCircle.MouseButton1Click:Connect(function()
    FloatCircle.Visible = false
    MainFrame.Position = FloatCircle.Position
    MainFrame.Visible = true
end)
