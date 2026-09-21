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
    TargetPart = "Head", -- "Head" hoặc "HumanoidRootPart" (Torso)
    OffAfterKill = false,
    ShowHP = false,
    FOVRadius = 150, -- Bán kính kiểm tra mục tiêu (studs)
    AutoLockOffDistance = 150,
    TeamCheck = true
}

local CurrentTarget = nil
local ESPFolder = Instance.new("Folder")
ESPFolder.Name = "FPS_ESP_Folder"
ESPFolder.Parent = Workspace

--------------------------------------------------------------------------------
-- CORE AIM ASSIST & HELPER FUNCTIONS
--------------------------------------------------------------------------------

-- Kiểm tra xem 2 player có thuộc cùng team hoặc không thể gây sát thương
local function IsTeammate(player)
    if not Config.TeamCheck then return false end
    if player.Team ~= nil and LocalPlayer.Team ~= nil then
        return player.Team == LocalPlayer.Team
    end
    return false
end

-- Kiểm tra mục tiêu hợp lệ trong tầm bắn
local function IsValidTarget(player)
    if player == LocalPlayer then return false end
    if IsTeammate(player) then return false end
    
    local character = player.Character
    if not character then return false end
    
    local humanoid = character:FindFirstChildOfClass("Humanoid")
    local targetPart = character:FindFirstChild(Config.TargetPart) or character:FindFirstChild("HumanoidRootPart")
    
    if not humanoid or humanoid.Health <= 0 then return false end
    if not targetPart then return false end
    
    return true, character, humanoid, targetPart
end

-- Tìm kẻ địch gần nhất trong bán kính Config.FOVRadius (3D Space)
local function GetNearestEnemy()
    local myChar = LocalPlayer.Character
    if not myChar then return nil end
    local myRoot = myChar:FindFirstChild("HumanoidRootPart")
    if not myRoot then return nil end
    
    local closestEnemy = nil
    local shortestDistance = Config.FOVRadius

    for _, player in ipairs(Players:GetPlayers()) do
        local valid, character, humanoid, targetPart = IsValidTarget(player)
        if valid then
            local dist = (targetPart.Position - myRoot.Position).Magnitude
            if dist <= shortestDistance then
                shortestDistance = dist
                closestEnemy = {
                    Player = player,
                    Character = character,
                    Humanoid = humanoid,
                    Part = targetPart,
                    Distance = dist
                }
            end
        end
    end

    return closestEnemy
end

-- Đếm số lượng kẻ địch đang sống trong khoảng cách 150 studs
local function GetEnemiesIn150Studs()
    local myChar = LocalPlayer.Character
    if not myChar then return 0 end
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
-- HIGH-SPEED AIM BOT ENGINE (RenderStepped Execution)
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
            -- Tự động kích hoạt lại nếu phát hiện kẻ địch đột ngột xuất hiện trong 150 studs
            if not Config.AimEnabled then
                Config.AimEnabled = true
            end
        end
    end

    -- Xử lý Ghim Tâm
    if Config.AimEnabled then
        local targetData = GetNearestEnemy()
        if targetData then
            CurrentTarget = targetData
            
            -- Tốc độ x10 Instant Lock (Không Delay): Cập nhật CFrame trực tiếp của Camera tới vị trí Target
            local targetPos = targetData.Part.Position
            local camPos = Camera.CFrame.Position
            
            -- Ép Camera nhìn thẳng vào vị trí mục tiêu ngay lập tức không phụ thuộc raycast hay màn hình
            Camera.CFrame = CFrame.new(camPos, targetPos)
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
-- DRAGGABLE & FLOATING GUI CREATION
--------------------------------------------------------------------------------
local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "FPS_AimAssist_UI"
ScreenGui.ResetOnSpawn = false
ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui")

-- Frame chính
local MainFrame = Instance.new("Frame")
MainFrame.Name = "MainFrame"
MainFrame.Size = UDim2.new(0, 240, 0, 320)
MainFrame.Position = UDim2.new(0.5, -120, 0.4, -160)
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

-- Nút Thu nhỏ (Minimize Button)
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

-- Floating Circle Button (Hiển thị khi GUI thu nhỏ)
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
-- DRAGGABLE LOGIC FOR MAIN FRAME & FLOATING CIRCLE
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
    btn.Size = UDim2.new(1, 0, 0, 35)
    btn.BackgroundColor3 = defaultState and Color3.fromRGB(0, 170, 100) or Color3.fromRGB(40, 40, 50)
    btn.Text = text .. ": " .. (defaultState and "ON" or "OFF")
    btn.TextColor3 = Color3.fromRGB(255, 255, 255)
    btn.Font = Enum.Font.GothamSemibold
    btn.TextSize = 12
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
local AimBtn = CreateToggleButton("Aim Assist Ultra", Config.AimEnabled, function(st)
    Config.AimEnabled = st
end)

-- 2. Target Body Part Selector
local TargetPartBtn = Instance.new("TextButton")
TargetPartBtn.Size = UDim2.new(1, 0, 0, 35)
TargetPartBtn.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
TargetPartBtn.Text = "Target Part: HEAD"
TargetPartBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
TargetPartBtn.Font = Enum.Font.GothamSemibold
TargetPartBtn.TextSize = 12
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

-- 3. Off After Kill Toggle
CreateToggleButton("Off/Auto-On (150 Studs)", Config.OffAfterKill, function(st)
    Config.OffAfterKill = st
end)

-- 4. Show HP Toggle
CreateToggleButton("Show HP (ESP)", Config.ShowHP, function(st)
    Config.ShowHP = st
end)

-- 5. Team Check Toggle
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
