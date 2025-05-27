---@diagnostic disable: undefined-field
--path = GetMapDataPath();
PATH = '/' .. GetMapDataPath() .. 'texts/';

function ExeCheck()
	errorHook(function()
		MessageBoxForPlayers(3, PATH .. 'wrong_exe.txt', 'ExitGame()');
	end)
	GetHeroCreatures(GetPlayerHeroes(1)[0], 259);
end

startThread(ExeCheck);
consoleCmd("dev_console_password = 'password'");

-- function LogTest()
--     consoleCmd("game_writelog 1")
--     print("=== LOG TEST BEGIN ===")
--     print("log_test")
--     print("=== LOG TEST END ===")
--     consoleCmd("game_writelog 0")
-- end
-- startThread(LogTest)

--SetWarfogBehaviour(0,0);
SetHeroesExpCoef(0)
Mode = GetDifficulty() + 1;

InfiniteLoop = true;


-- 1 - wybieranie
-- 2 - banowanie
-- 3 - banowanie + blokowanie ?????? (obecnie full random)
-- 4 - matchup

GameBegin1 = 0;
GameBegin2 = 0;

Ban = {0, 0}

Hero0 = { GetPlayerHeroes(PLAYER_1)[0], GetPlayerHeroes(PLAYER_2)[0] }
HeroRace = { 0, 0 }
Town = {"Town_Player_1", "Town_Player_2"}

SetObjectOwner(Town[1], 0)
SetObjectOwner(Town[2], 0)

SkillsAmmount = 236

FirstDay = 0;

SpShopGold = 10000;
ShrineGold = 6000;

-- NecroLeadershipAttack = {1, 1, 0}
-- NecroLeadershipDefence = {0, 0, 2}
-- NecroLeadershipLevel = {0, 0}

MovementAdd = {-10000, -10000}

ChangeHeroStat(Hero0[1], 7, -5000)
ChangeHeroStat(Hero0[2], 7, -5000)

OpenCircleFog(42, 48, 0, 15, PLAYER_1)
OpenCircleFog(38, 87, 0, 12, PLAYER_2)

PERK_RAISE_ARCHERS = 223;
NECROMANCER_FEAT_HERALD_OF_DEATH = 224;
PERK_FORTUNATE_ADVENTURER = 225;
KNIGHT_FEAT_GUARDIAN_ANGEL = 226;

---combines two arrays
---@param ar1 any
---@param ar1l integer
---@param ar2 any
---@param ar2l integer
---@return any
function ArrayCon (ar1, ar1l, ar2, ar2l)
	for i=1, ar2l, 1 do
		ar1[ar1l + i] = ar2[i];
	end
	return ar1;
end

-- function Test()
-- 	OpenCircleFog(0, 0, 0, 9999, 1)
-- 	OpenCircleFog(0, 0, 1, 9999, 1)
-- 	if IsObjectExists(Hero0[2]) then
-- 		SetObjectOwner(Hero0[2], 1)
-- 	end
-- 	if IsObjectExists(Hero1[2]) then
-- 		SetObjectOwner(Hero1[2], 1)
-- 	end
-- end

function GetLvlStat(faction)
    local random_stat = random(100)+1;
    local stat;
    if random_stat <= LvlUpStatsPercent[faction][1] then
        stat = 1;
    elseif random_stat <= LvlUpStatsPercent[faction][1] + LvlUpStatsPercent[faction][2] then
        stat = 2;
    elseif random_stat <= LvlUpStatsPercent[faction][1] + LvlUpStatsPercent[faction][2] + LvlUpStatsPercent[faction][3] then
        stat = 3;
    else
        stat = 4;
    end
    return stat;
end


---@param player integer
---@return integer
function Opponent(player)
	return (player-3)*(-1)
end


---@param textPath string
---@param hero string
---@param player integer
function ShowFlyingSignDefault(textPath, hero, player)
	ShowFlyingSign(textPath, hero, player, 3.0)
end

---@param hero string
---@param player integer
---@return integer
function GetHeroFactionalSkillMastery(hero, player)
	local race = HeroRace[player];
	local skill = FactionalSkills[race];
	local m = GetHeroSkillMastery(hero, skill);
	if (HasArtefact(hero, ARTIFACT_PEDANT_OF_MASTERY, 0) == 1) and (HasArtefact(hero, ARTIFACT_PEDANT_OF_MASTERY, 1) == 0) then
		m = m + 1;
	end
	return m;
end


---@param hero string
---@param name string
---@return boolean
function IsHero(hero, name)
	if hero == name or hero == name .. "2"then
		return true;
	else
		return false;
	end
end

---Returns array length
---@param array any
---@return integer
function Len(array)
	if array.n ~= nil then
		return array.n;
	end
    local n = 1;
    while array[n] ~= nil do
        n = n * 2;
    end
    local m = n / 4;
    n = n - m;
    while m > 0 do
        if array[n] ~= nil then
            n = n + m;
        else
            n = n - m;
        end
        m = m / 2;
    end
    return n;
end

---Adds element at end of array
---@param array any
---@param value any
function Append(array, value)
    local l = Len(array);
    array[l+1] = value;
	if array.n ~= nil then
		array.n = array.n + 1;
	end
end

---Returns random element of array
---@param array any
---@return any
function RandElement(array)
    return array[random(Len(array))+1];
end


---Returns random element of array and removes it from array
---@param array any
---@return any
function RandElementRemove(array)
	local len = Len(array);
	local index = random(len)+1;
	local value = array[index];
	for i = index, len-1, 1 do
		array[i] = array[i+1];
	end
	array[len] = nil;
	-- array.n = array.n - 1;
	array.n = len - 1;
    return value;
end

function ChangeHeroResources(player, resource, quantity)
	SetPlayerResource(player, resource, GetPlayerResource(player, resource) + quantity);
end

function GetMagicSchoolSkillId(school)
	if school == SPELLS_DESTRUCTIVE then return SKILL_DESTRUCTIVE_MAGIC end
	if school == SPELLS_DARK then return SKILL_DARK_MAGIC end
	if school == SPELLS_LIGHT then return SKILL_LIGHT_MAGIC end
	if school == SPELLS_SUMMONING then return SKILL_SUMMONING_MAGIC end
	if school == SPELLS_RUNES then return HERO_SKILL_RUNELORE end
	return 0
end


function GiveResources(player, resource, ammount)
	local hero = Hero1[player];
	SetPlayerResource(player, resource, GetPlayerResource(player, resource) + ammount);
	-- if ammount > 0 then
	-- 	ammount = "+"..ammount
	-- end
	local msg = {
		PATH .. 'ResourcesGive.txt';
		ammount = ammount,
		resource = ResourcesNames[resource]
	}
	ShowFlyingSign(msg, hero, player, 3.0)
end

function SpellsColors(school)
	local name = "";
	if school == SPELLS_DESTRUCTIVE then name = "Destructive";
	elseif school == SPELLS_DARK then name = "Dark";
	elseif school == SPELLS_LIGHT then name = "Light";
	elseif school == SPELLS_SUMMONING then name = "Summoning";
	elseif school == SPELLS_WARCRIES then name = "Warcries";
	end
	return PATH.."SpellsColors/" .. name .. ".txt";
end


function TeachSpellInfo(hero, player, school, spell)
	TeachHeroSpell(hero, SPELLS[school][spell].id);
	HeroSpells[player][school][spell] = 1;
	local msg = {
		PATH .. 'TeachSpell.txt';
		spell = SPELLS[school][spell].name,
		school = SpellsColors(school)
	}
	ShowFlyingSign(msg, hero, player, 3.0)
end

function GetPlayer(hero)
	if Hero1[1] == hero then return 1
	elseif Hero1[2] == hero then return 2
	end
	return 0
end

function GetStatName(stat)
	local s = "";
	if stat == STAT_ATTACK then s = "Offence";
	elseif stat == STAT_DEFENCE then s = "Defence";
	elseif stat == STAT_SPELL_POWER then s = "SpellPower";
	elseif stat == STAT_KNOWLEDGE then s = "Knowledge";	
	end
	return "/GameMechanics/RefTables/HeroAttribute/"..s..".txt";
end

function GiveHeroStat(hero, stat, ammount)
	local player = GetPlayer(hero);
	ChangeHeroStat(hero, stat, ammount);
	local msg = {
		PATH .. 'GiveStat.txt';
		stat = GetStatName(stat),
		ammount = ammount
	}
	ShowFlyingSign(msg, hero, player, 3.0)

end

-- function TeachSpellAndUpdateDB(hero, player, spell, school)
-- 	TeachHeroSpell(hero, spell);
-- 	UpdateSpells(spell, player, 0, 5);
-- end


-- =====================================================================================================================================================
-- Ban
-- =====================================================================================================================================================

Towns = {
"/Text/Game/Towns/Types/heaven.txt",
"/Text/Game/Towns/Types/inferno.txt",
"/Text/Game/Towns/Types/necromancy.txt",
"/Text/Game/Towns/Types/preserve.txt",
"/Text/Game/Towns/Types/academy.txt",
"/Text/Game/Towns/Types/dungeon.txt",
"/Text/Game/Towns/Types/fortress.txt",
"/Text/Game/Towns/Types/stronghold.txt",
PATH .. "Random_Town.txt",
--PATH .. "Random_Town2.txt",
}

ResourcesNames = {
	[WOOD] = "/Text/Game/Treasures/Wood/Name.txt",
	[ORE] = "/Text/Game/Treasures/Ore/Name.txt",
	[MERCURY] = "/Text/Game/Treasures/Mercury/Name.txt",
	[CRYSTAL] = "/Text/Game/Treasures/Crystals/Name.txt",
	[SULFUR] = "/Text/Game/Treasures/Sulfur/Name.txt",
	[GEM] = "/Text/Game/Treasures/Gems/Name.txt",
	[GOLD] = "/Text/Game/Treasures/Gold/Name.txt"
}

FactionalSkills = {
	SKILL_TRAINING,
	SKILL_GATING,
	SKILL_NECROMANCY,
	SKILL_AVENGER,
	SKILL_ARTIFICIER,
	SKILL_INVOCATION,
	HERO_SKILL_RUNELORE,
	HERO_SKILL_DEMONIC_RAGE
}

--------     HAVEN     INF    NECR     ELF    MAGE    LIGA    GNOM     ORC
Woods    = {     0,      0,      0,      0,     0,      0,     10,      0};
Ores     = {     0,      0,      0,      0,     0,      0,     10,      0};
Mercurys = {     0,      0,      0,      0,     0,      0,      7,      0};
Crystals = {     0,      0,      0,      0,     0,      0,      7,      0};
Sulfurs  = {     0,      0,      0,      0,     0,      0,      7,      0};
Gems     = {     0,      0,      0,      0,     0,      0,      7,      0};
Golds    = {  2000,   2000,   2000,   2000,   2000,   2000,   2000,   2000};


RandSkill = {
{1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 1},--haven
{1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 12, 12, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 2},--inferno
{1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 5, 5, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 3},--necropolis
{1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 4},--sylvan
{1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 5},--academy
{1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 6},--dungeon
{1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 7},--fortress
{1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 183, 187, 187, 187, 187, 187, 187, 191, 191, 191, 191, 191, 191, 195, 195, 195, 195, 195, 195, 199, 199, 199, 199, 199, 199, 203, 203, 203, 203, 203, 203, 172, 172, 172, 172, 172, 172, 172, 172, 172, 172, 8}--stronghold
}



DiplomacyCreatures = {13, 14, 112, 27, 28, 137, 41, 42, 158, 55, 56, 151, 69, 70, 165, 83, 84, 144, 104, 105, 172, 129, 130, 179}

RecruitmentCreatures = {
{1, 2, 106, 15, 16, 131, 29, 30, 152, 43, 44, 145, 57, 58, 159, 71, 72, 138, 92, 93, 166, 117, 118, 173},
{3, 4, 107, 17, 18, 132, 31, 32, 153, 45, 46, 146, 59, 60, 160, 73, 74, 139, 94, 95, 167, 119, 120, 174},
{5, 6, 108, 19, 20, 133, 33, 34, 154, 47, 48, 147, 61, 62, 161, 75, 76, 140, 96, 97, 168, 121, 122, 175},
}

SylvanUnits = { 43, 44, 145, 45, 46, 146, 47, 48, 147, 49, 50, 148, 51, 52, 149, 53, 54, 150, 55, 56, 151 };

Minor = {1, 3, 5, 8, 10, 12, 14, 16, 18, 20, 24, 26, 27, 29, 32, 34, 35, 55, 56, 58, 60, 61, 62, 64, 65, 66, 70, 80, 84, 87, 90}
Minor.n = 31;
Major = {33, 2, 4, 9, 17, 19, 21, 23, 25, 28, 31, 36, 37, 38, 39, 40, 41, 42, 43, 52, 57, 59, 63, 71, 74, 75, 81, 82, 85, 86, 88, 93, 94, 95}
Major.n = 33;

LvlUpStatsPercent = { --atk, def, sp, kn
{30, 45, 10, 15}, --hum
{45, 10, 15, 30}, --inf
{10, 30, 45, 15}, --nec
{15, 45, 10, 30}, --sylv
{10, 15, 30, 45}, --aca
{30, 10 ,45, 15}, --dung
{20, 30, 30, 20}, --fortr
{45, 35,  5, 15}, --strong
}

AvengerUnits = { { 0, 0, 0, 0, 0, 0, 0 }, {0, 0, 0, 0, 0, 0, 0 } };
AvengerUnitsCount = { { 0, 0, 0, 0, 0, 0, 0 }, {0, 0, 0, 0, 0, 0, 0 } };

ArfitacterResources = {{25, 15}, {45, 35}, {60, 50}, {1000, 1000}};

FACTION_HEAVEN = 1
FACTION_INFERNO = 2
FACTION_NECROPOLIS = 3
FACTION_SYLVAN = 4
FACTION_ACADENY = 5
FACTION_DUNGEON = 6
FACTION_FORTRESS = 7
FACTION_STRONGHOLD = 8
FACTION_SPECIAL = 9

HEROES = {

	[FACTION_HEAVEN] = {
		--{name = "Dougal", ico = "hero_1_1_"},
		{name = "Duncan", ico = "hero_2_1_"},
		{name = "Laszlo", ico = "hero_3_1_"},
		-- {name = "Rutger", ico = "hero_4_1_"},
		{name = "Ornella", ico = "hero_5_1_"},
		{name = "Irina", ico = "hero_6_1_"},
		{name = "Ellaine", ico = "hero_7_1_"},
		{name = "Vittorio", ico = "hero_8_1_"},
		{name = "Godric", ico = "hero_9_1_"},
		{name = "Alaric", ico = "hero_10_1_"},
		{name = "Isabell", ico = "hero_11_1_"},
		{name = "Freyda", ico = "hero_12_1_"},
		{name = "Gabrielle", ico = "hero_13_1_"},
		-- {name = "", ico = "hero_14_1_"},
	},
    
    [FACTION_INFERNO] = {
		{name = "Grok", ico = "hero_1_2_"},
		{name = "Jezebeth", ico = "hero_2_2_"},
		{name = "Marbas", ico = "hero_3_2_"},
		{name = "Nebiros", ico = "hero_4_2_"},
		{name = "Alastor", ico = "hero_5_2_"},
		{name = "Deleb", ico = "hero_6_2_"},
		{name = "Grawl", ico = "hero_7_2_"},
		{name = "Nymus", ico = "hero_8_2_"},
		{name = "Orlando", ico = "hero_9_2_"},
		{name = "Agrael", ico = "hero_10_2_"},
		{name = "Sovereign", ico = "hero_11_2_"},
		{name = "Biara", ico = "hero_12_2_"},
		-- {name = "", ico = "hero_13_2_"},
		-- {name = "", ico = "hero_14_2_"},
	},
    
    [FACTION_NECROPOLIS] = {
		{name = "Deirdre", ico = "hero_1_3_"},
		-- {name = "Lucretia", ico = "hero_2_3_"},
		{name = "Naadir", ico = "hero_3_3_"},
		-- {name = "Zoltan", ico = "hero_4_3_"},
		{name = "Orson", ico = "hero_5_3_"},
		{name = "Raven", ico = "hero_6_3_"},
		{name = "Vladimir", ico = "hero_7_3_"},
		{name = "Kaspar", ico = "hero_8_3_"},
		{name = "Arantir", ico = "hero_9_3_"},
		{name = "OrnellaNecro", ico = "hero_10_3_"},
		{name = "Markal", ico = "hero_11_3_"},
		{name = "NicolaiNecro", ico = "hero_12_3_"},
		{name = "Giovanni", ico = "hero_13_3_"},
		-- {name = "", ico = "hero_14_3_"},
	},
    
	[FACTION_SYLVAN] = {
		{name = "Anwen", ico = "hero_1_4_"},
		{name = "Gilraen", ico = "hero_2_4_"},
		{name = "Talanar", ico = "hero_3_4_"},
		{name = "Dirael", ico = "hero_4_4_"},
		{name = "Ossir", ico = "hero_5_4_"},
		{name = "Ylthin", ico = "hero_6_4_"},
		{name = "Vinrael", ico = "hero_7_4_"},
		{name = "Wyngaal", ico = "hero_8_4_"},
		{name = "Findan", ico = "hero_9_4_"},
		{name = "Alaron", ico = "hero_10_4_"},
		{name = "Tieru", ico = "hero_11_4_"},
		-- {name = "", ico = "hero_12_4_"},
		-- {name = "", ico = "hero_13_4_"},
		-- {name = "", ico = "hero_14_4_"},
	},
    
	[FACTION_ACADENY] = {
		{name = "Faiz", ico = "hero_1_5_"},
		{name = "Havez", ico = "hero_2_5_"},
		{name = "Nathir", ico = "hero_3_5_"},
		{name = "Nur", ico = "hero_4_5_"},
		{name = "Jhora", ico = "hero_5_5_"},
		{name = "Narxes", ico = "hero_6_5_"},
		{name = "Galib", ico = "hero_7_5_"},
		{name = "Razzak", ico = "hero_8_5_"},
		{name = "Zehir", ico = "hero_9_5_"},
		{name = "Maahir", ico = "hero_10_5_"},
		{name = "Cyrus", ico = "hero_11_5_"},
		-- {name = "Temkhan", ico = "hero_12_5_"},
		-- {name = "", ico = "hero_13_5_"},
		-- {name = "", ico = "hero_14_5_"},
	},
    
	[FACTION_DUNGEON] = {
		{name = "Eruina", ico = "hero_1_6_"},
		{name = "Sinitar", ico = "hero_2_6_"},
		-- {name = "Yrwanna", ico = "hero_3_6_"},
		{name = "Yrbeth", ico = "hero_4_6_"},
		{name = "Kythra", ico = "hero_5_6_"},
		{name = "Lethos", ico = "hero_6_6_"},
		{name = "Sorgal", ico = "hero_7_6_"},
		{name = "Vayshan", ico = "hero_8_6_"},
		{name = "Raelag", ico = "hero_9_6_"},
		{name = "Shadya", ico = "hero_10_6_"},
		{name = "Ylaya", ico = "hero_11_6_"},
		{name = "Thralsai", ico = "hero_12_6_"},
		{name = "Agbeth", ico = "hero_13_6_"},
		-- {name = "", ico = "hero_14_6_"},
	},
    
	[FACTION_FORTRESS] = {
		{name = "Brand", ico = "hero_1_7_"},
		{name = "Ebba", ico = "hero_2_7_"},
		-- {name = "Erling", ico = "hero_3_7_"},
		{name = "Helmar", ico = "hero_4_7_"},
		{name = "Inga", ico = "hero_5_7_"},
		{name = "Ingvar", ico = "hero_6_7_"},
		{name = "Svea", ico = "hero_7_7_"},
		{name = "Karli", ico = "hero_8_7_"},
		{name = "KingTolghar", ico = "hero_9_7_"},
		{name = "Wulfstan", ico = "hero_10_7_"},
		{name = "Rolf", ico = "hero_11_7_"},
		{name = "Hangvul", ico = "hero_12_7_"},
		-- {name = "", ico = "hero_13_7_"},
		-- {name = "", ico = "hero_14_7_"},
	},
    
	[FACTION_STRONGHOLD] = {
		{name = "Urghat", ico = "hero_1_8_"},
		{name = "Garuna", ico = "hero_2_8_"},
		{name = "ShakKarukat", ico = "hero_3_8_"},
		{name = "Telsek", ico = "hero_4_8_"},
		{name = "Haggash", ico = "hero_5_8_"},
		{name = "Kragh", ico = "hero_6_8_"},
		{name = "Kilghan", ico = "hero_7_8_"},
		{name = "Gorshak", ico = "hero_8_8_"},
		{name = "Kujin", ico = "hero_9_8_"},
		{name = "Gotai", ico = "hero_10_8_"},
		{name = "Quroq", ico = "hero_11_8_"},
		-- {name = "Kunyak", ico = "hero_12_8_"},
		-- {name = "", ico = "hero_13_8_"},
		-- {name = "", ico = "hero_14_8_"}
	},
	[FACTION_SPECIAL] = {
		{name = "SC_1", ico = ""},
		{name = "SC_2", ico = ""},
		{name = "WC_1", ico = ""},
		{name = "WC_2", ico = ""},
	}
}

HEROES[FACTION_HEAVEN].n = 11;
HEROES[FACTION_INFERNO].n = 12;
HEROES[FACTION_NECROPOLIS].n = 11;
HEROES[FACTION_SYLVAN].n = 11;
HEROES[FACTION_ACADENY].n = 11;
HEROES[FACTION_DUNGEON].n = 12;
HEROES[FACTION_FORTRESS].n = 11;
HEROES[FACTION_STRONGHOLD].n = 11;
HEROES[FACTION_SPECIAL].n = 4;

GoldTaken = { 0, 0 }

SPELLS_DESTRUCTIVE = 0;
SPELLS_DARK = 1;
SPELLS_LIGHT = 2;
SPELLS_SUMMONING = 3;
SPELLS_RUNES = 4;
SPELLS_WARCRIES = 5;

SpellsAmmount = {
	[SPELLS_DESTRUCTIVE] = 11,
	[SPELLS_DARK] = 10,
	[SPELLS_LIGHT] = 10,
	[SPELLS_SUMMONING] = 11,
	[SPELLS_RUNES] = 10,
	[SPELLS_WARCRIES] = 6
} 

SPELLS = {
	[SPELLS_DESTRUCTIVE] = {
		{id = 1,	level = 1,	ico = "spell_3_2_",	name = "/Text/Game/Spells/Combat/Magic_Arrow/name.txt"}, -- magiczna strzaĹ‚a
		{id = 237,	level = 1,	ico = "spell_3_1_",	name = "/Text/Game/Spells/Combat/StoneSpikes/name.txt"}, -- kamienne kolce

		{id = 3,	level = 2,	ico = "spell_3_4_",	name = "/Text/Game/Spells/Combat/Lightning_Bolt/name.txt"}, -- bĹ‚yskawica
		{id = 4,	level = 2,	ico = "spell_3_3_",	name = "/Text/Game/Spells/Combat/Ice_Bolt/name.txt"}, -- lodowy promieĹ„

		{id = 5,	level = 3,	ico = "spell_3_7_",	name = "/Text/Game/Spells/Combat/Fireball/name.txt"}, -- kula ognia
		{id = 6,	level = 3,	ico = "spell_3_5_",	name = "/Text/Game/Spells/Combat/Frost_Ring/name.txt"}, -- krÄ…g zimna
		{id = 236,	level = 3,	ico = "spell_3_6_",	name = "/Text/Game/Spells/Combat/Firewall/name.txt"}, -- Ĺ›ciana ognia 

		{id = 7,	level = 4,	ico = "spell_3_8_",	name = "/Text/Game/Spells/Combat/Chain_Lightning/name.txt"}, -- Ĺ‚aĹ„cuch bĹ‚yskawic
		{id = 8,	level = 4,	ico = "spell_3_9_",	name = "/Text/Game/Spells/Combat/Meteor_Shower/name.txt"}, -- grad meteorytĂłw 

		{id = 9,	level = 5,	ico = "spell_3_11_",	name = "/Text/Game/Spells/Combat/Implosion/name.txt"}, -- implozja
		--{id = 10,	level = 5,	ico = "spell_3_12_",	name = "/Text/Game/Spells/Combat/Armageddon/name.txt"}, -- armagedon
		{id = 279,	level = 5,	ico = "spell_3_10_",	name = "/Text/Game/Spells/Combat/DeepFreeze/name.txt"}, -- gĹ‚ebokie zamroĹĽenie 
	},


	[SPELLS_DARK] = {
		
		{id = 11,	level = 1,	ico = "spell_2_2_",	name = "/Text/Game/Spells/Combat/Curse/name.txt"}, -- osĹ‚abienie
		{id = 12,	level = 1,	ico = "spell_2_3_",	name = "/Text/Game/Spells/Combat/Slow/name.txt"}, -- spowolnienie

		{id = 13,	level = 2,	ico = "spell_2_4_",	name = "/Text/Game/Spells/Combat/Disrupting_Ray/name.txt"}, -- wraĹĽliwoĹ›Ä‡
		{id = 14,	level = 2,	ico = "spell_2_5_",	name = "/Text/Game/Spells/Combat/Plague/name.txt"}, -- rozkĹ‚ad
		
		{id = 15,	level = 3,	ico = "spell_2_7_",	name = "/Text/Game/Spells/Combat/Weakness/name.txt"}, -- cierpienie
		{id = 17,	level = 3,	ico = "spell_2_6_",	name = "/Text/Game/Spells/Combat/Forgetfulness/name.txt"}, -- dezorientacja

		{id = 19,	level = 4,	ico = "spell_2_8_",	name = "/Text/Game/Spells/Combat/Blind/name.txt"}, -- oĹ›lepienie
		--{id = 277,	level = 4,	ico = "spell_2_1_",	name = "/GameMechanics/Spell/Combat_Spells/DarkMagic/Sorrow/SorrowName.txt"}, -- smutek
		{id = 278,	level = 4,	ico = "spell_2_10_",	name = "/Text/Game/Spells/Combat/Vampirism/name.txt"}, -- wampiryzm

		{id = 18,	level = 5,	ico = "spell_2_9_",	name = "/Text/Game/Spells/Combat/Berserk/name.txt"}, -- szaĹ‚
		{id = 20,	level = 5,	ico = "spell_2_11_",	name = "/Text/Game/Spells/Combat/Hypnotize/name.txt"}, -- hipnoza
		--{id = 21,	level = 5,	ico = "spell_2_12_",	name = "/Text/Game/Spells/Combat/Unholy_Word/name.txt"}, -- klÄ…twa piekieĹ‚
	},

	[SPELLS_LIGHT] = {

		{id = 23,	level = 1,	ico = "spell_1_1_",	name = "/Text/Game/Spells/Combat/Bless/name.txt"}, -- boska siĹ‚a
		{id = 29,	level = 1,	ico = "spell_1_6_",	name = "/Text/Game/Spells/Combat/Deflect_Arrows/name.txt"}, -- odbicie pocisku

		{id = 25,	level = 2,	ico = "spell_1_3_",	name = "/Text/Game/Spells/Combat/Stoneskin/name.txt"}, -- wytrzymaloĹ›Ä‡
		{id = 24,	level = 2,	ico = "spell_1_2_",	name = "/Text/Game/Spells/Combat/Haste/name.txt"}, -- przyspieszenie

		{id = 26,	level = 3,	ico = "spell_1_5_",	name = "/Text/Game/Spells/Combat/Dispel/name.txt"}, -- oczyszczenie
		{id = 28,	level = 3,	ico = "spell_1_7_",	name = "/Text/Game/Spells/Combat/Bloodlust/name.txt"}, -- prawa moc

		{id = 31,	level = 4,	ico = "spell_1_9_",	name = "/Text/Game/Spells/Combat/Anti-magic/name.txt"}, -- antymagia
		{id = 32,	level = 4,	ico = "spell_1_8_",	name = "/Text/Game/Spells/Combat/Teleport/name.txt"}, -- teleport
		--{id = 281,	level = 4,	ico = "spell_1_10_",	name = "/Text/Game/Spells/Combat/DivineVengeance/name.txt"}, -- boska zemsta

		--{id = 35,	level = 5, ico = "spell_1_12_",name = "/Text/Game/Spells/Combat/Holy_Word/name.txt"}, -- sĹ‚owo Ĺ›wiatĹ‚a
		{id = 48,	level = 5,	ico = "spell_1_11_",	name = "/Text/Game/Spells/Combat/Resurrect/name.txt"}, -- wskrzeszenie
		{id = 280,	level = 5,	ico = "spell_1_4_",	name = "/Text/Game/Spells/Combat/Regeneration/name.txt"}, -- regenracja

	},

	[SPELLS_SUMMONING] = {

		{id = 2,	level = 1,	ico = "spell_4_1_",	name = "/Text/Game/Spells/Combat/Magic_Fist/name.txt"}, -- pieĹ›Ä‡ gniewu
		{id = 38,	level = 1,	ico = "spell_4_2_",	name = "/Text/Game/Spells/Combat/Land_Mine/name.txt"}, -- ogniste puĹ‚apki

		{id = 39,	level = 2,	ico = "spell_4_3_",	name = "/Text/Game/Spells/Combat/Wasp_Swarm/name.txt"}, -- rĂłj os
		{id = 42,	level = 2,	ico = "spell_4_4_",	name = "/Text/Game/Spells/Combat/Animate_Dead/name.txt"}, -- wskrzeĹ› umarĹ‚ych
		{id = 282,	level = 2,	ico = "spell_4_5_",	name = "/Text/Game/Spells/Combat/ArcaneCrystal/name.txt"}, -- magiczny krysztaĹ‚

		{id = 40,	level = 3,	ico = "spell_4_6_",	name = "/Text/Game/Spells/Combat/Phantom/name.txt"}, -- widmowe zastÄ™py
		--{id = 41,	level = 3,	ico = "spell_4_8_",	name = "/Text/Game/Spells/Combat/Earthquake/name.txt"}, -- trzÄ™sienie ziemi
		{id = 284,	level = 3,	ico = "spell_4_7_",	name = "/Text/Game/Spells/Combat/BladeBarrier/name.txt"}, -- bariera miecza

		{id = 43,	level = 4,	ico = "spell_4_9_",	name = "/Text/Game/Spells/Combat/Summon_Elementals/name.txt"}, -- przywoĹ‚anie ĹĽywioĹ‚akĂłw
		{id = 283,	level = 4,	ico = "spell_4_10_",	name = "/Text/Game/Spells/Combat/SummonHive/name.txt"}, -- gniazdo os

		{id = 34,	level = 5,	ico = "spell_4_12_",	name = "/Text/Game/Spells/Combat/Celestial_Shield/name.txt"}, -- tajemna zbroja
		{id = 235,	level = 5,	ico = "spell_4_11_",	name = "/Text/Game/Spells/Combat/ConjurePhoenix/name.txt"}, -- przywoĹ‚anie feniksa
	},
	
	[SPELLS_RUNES] = {
		{id = 249,	level = 1, ico = "spell_5_1_",	name = "GameMechanics/Spell/Combat_Spells/RunicMagic/RuneOfChargeText.txt"}, -- runa szarĹĽy
		{id = 250,	level = 1, ico = "spell_5_2_",	name = "GameMechanics/Spell/Combat_Spells/RunicMagic/RuneOfBerserkingName.txt"}, -- runa berserkera

		{id = 251,	level = 2, ico = "spell_5_3_",	name = "GameMechanics/Spell/Combat_Spells/RunicMagic/RuneOfMagicControlName.txt"}, -- runa magicznej kontroli
		{id = 252,	level = 2, ico = "spell_5_4_",	name = "GameMechanics/Spell/Combat_Spells/RunicMagic/RuneOfExorcismName.txt"}, -- runa egzorcyzmĂłw

		{id = 253,	level = 3, ico = "spell_5_5_",	name = "GameMechanics/Spell/Combat_Spells/RunicMagic/RuneOfElementalImmunityName.txt"}, -- runa odpornoĹ›ci na ĹĽywioĹ‚y
		{id = 256,	level = 3, ico = "spell_5_6_",	name = "GameMechanics/Spell/Combat_Spells/RunicMagic/RuneOfEthrealnessName.txt"}, -- runa niematerialnoĹ›ci

		{id = 254,	level = 4, ico = "spell_5_7_",	name = "GameMechanics/Spell/Combat_Spells/RunicMagic/RuneOfStunningName.txt"}, -- runa piorunowĹ‚adna
		{id = 257,	level = 4, ico = "spell_5_8_",	name = "GameMechanics/Spell/Combat_Spells/RunicMagic/RuneOfReviveName.txt"}, -- runa wskrzeszenia

		{id = 255,	level = 5, ico = "spell_5_10_",	name = "GameMechanics/Spell/Combat_Spells/RunicMagic/RuneOfBattleRageName.txt"}, -- runa szaĹ‚u bojowego
		{id = 258,	level = 5, ico = "spell_5_9_",	name = "GameMechanics/Spell/Combat_Spells/RunicMagic/RuneOfDragonFormName.txt"}, -- runa smoczej siĹ‚y
	},
	
	[SPELLS_WARCRIES] = {
		{id = 290,	level = 1,	ico = "spell_6_1_",	name = "Text/Game/Spells/Hero_Special_Abilities/Warcry_RallingCry/Name.txt"}, -- pokrzepiajÄ…cve zawoĹ‚anie
		{id = 291,	level = 1,	ico = "spell_6_2_",	name = "Text/Game/Spells/Hero_Special_Abilities/Warcry_CallOfBlood/Name.txt"}, -- zew krwii
		{id = 292,	level = 2,	ico = "spell_6_3_",	name = "Text/Game/Spells/Hero_Special_Abilities/Warcry_WordOfTheChief/Name.txt"}, --	sĹ‚owo wodza
		{id = 293,	level = 2,	ico = "spell_6_4_",	name = "Text/Game/Spells/Hero_Special_Abilities/Warcry_FearMyRoar/Name.txt"}, --	drĹĽyj przed mym rykiem
		{id = 294,	level = 3,	ico = "spell_6_5_",	name = "Text/Game/Spells/Hero_Special_Abilities/Warcry_BattleCry/Name.txt"}, --	bitewne zawoĹ‚anie
		{id = 295,	level = 3,	ico = "spell_6_6_",	name = "Text/Game/Spells/Hero_Special_Abilities/Warcry_ShoutOfMany/Name.txt"}, -- gniew hordy

	}
}

--for i=1, 6, 1 do
--	i2 = true;
--	for i1=1, i2, 1 do
--		SpellsAmmount[i] = SpellsAmmount[i] + 1;
--		if SPELLS[i][i1]["id"] == nil then i2 = false end
--	end
--end


function GetSpellsToLearn (magic_id, min_level, max_level, id)
	local spells = {};
	local spell_l_id = 0;
	local lvl = min_level;
	local i = 1;
	lvl = SPELLS[magic_id][i]["level"];
	while lvl <= max_level and i <= SpellsAmmount[magic_id] do
		lvl = SPELLS[magic_id][i]["level"];
		if lvl >= min_level and lvl <= max_level then
			if not (HeroSpells[id][magic_id][i] == 1) then
				spell_l_id = spell_l_id + 1;
				spells[spell_l_id] = SPELLS[magic_id][i]["id"];
			end
		end
		i=i+1;
	end
	return spell_l_id, spells;
end


function GetInternalSpellsIdToLearn (magic_id, min_level, max_level, id)
	local spells = {};
	local spell_l_id = 0;
	local lvl = min_level;
	local i = 1;
	lvl = SPELLS[magic_id][i]["level"];
	while lvl <= max_level and i <= SpellsAmmount[magic_id] do
		lvl = SPELLS[magic_id][i]["level"];
		if lvl >= min_level and lvl <= max_level then
			if not (HeroSpells[id][magic_id][i] == 1) then
				spell_l_id = spell_l_id + 1;
				spells[spell_l_id] = i;
			end
		end
		i=i+1;
	end
	return spell_l_id, spells;
end



function UpdateSpells (spell_id, id, magic_min, magic_max)
	for i = magic_min, magic_max, 1 do
		for i1 = 1, SpellsAmmount[i], 1 do
			if SPELLS[i][i1]["id"] == spell_id then
				HeroSpells[id][i][i1] = 1;
				return 0;
			end
		end
	end
	return 1;
end


function QuestionNo ()

end

-- destructive, dark, light, summomoning, runic
--SPELLS[1][1]["id"]

HeroSpells = {

	{

		[SPELLS_DESTRUCTIVE] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},

		[SPELLS_DARK] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},

		[SPELLS_LIGHT] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},

		[SPELLS_SUMMONING] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
		
		[SPELLS_RUNES] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
		
		[SPELLS_WARCRIES] = {
		0, 0, 0, 0, 0, 0},
		
		
	},

	{

		[SPELLS_DESTRUCTIVE] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},

		[SPELLS_DARK] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},

		[SPELLS_LIGHT] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},

		[SPELLS_SUMMONING] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
		
		[SPELLS_RUNES] = {
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
		
		[SPELLS_WARCRIES] = {
		0, 0, 0, 0, 0, 0},		
	}

}


--hero_warcries = {
--	{0, 0, 0, 0, 0, 0},
--	{0, 0, 0, 0, 0, 0}
--};




ObjectsToBan1 = { "hav1", "inf1", "nec1", "syl1", "aca1", "dun1", "for1", "str1", "neu1" }
ObjectsToBan2 = { "hav2", "inf2", "nec2", "syl2", "aca2", "dun2", "for2", "str2", "neu2" }

for i=1, 2, 1 do
	for i1=1, 6, 1 do
		SetObjectEnabled("red" .. i .. "_" .. i1, nil)
		SetObjectEnabled("blue" .. i .. "_" .. i1, nil)
	end
end

GlobalClockWork = 0;

GlobalTime = 1;

function GlobalClock ()
	while GlobalClockWork == 0 do
		GlobalTime=GlobalTime+1;
		sleep(1)
		GlobalTime=GlobalTime+1;
		sleep(1)
		GlobalTime=GlobalTime+1;
		sleep(1)
		GlobalTime=GlobalTime+1;
		sleep(1)
		GlobalTime=GlobalTime+1;
		sleep(1)
		if GlobalTime > 100 then
			GlobalTime = 10;
		end		
		random(8);
		
	end
	return 0;
end



startThread(GlobalClock);

function RandomClock (random_max)
	local random_1 = GlobalTime;
	if random_1 <= 40 then
		random_1 = abs(random_1 - mod(random_1, 40));
	end 
	local random_2 = 1;
	for i=1, random_1, 1 do
		local random_2 = random_2 + random(random_max);
	end
	local mod_rand = mod(random_2, random_max * 2)
	
	local rand = random(100 + random_max * 2 + GlobalTime * 2 + random(5) * 10 + mod_rand);
	local rand2 = mod(rand, random_max)
	return rand2;

end

function Visited(hero)
	ShowFlyingSign("/Text/Game/BuildingsCommon/AlreadyVisited.txt", hero, GetObjectOwner(hero), 3.0);
end

function SafeRemoveObject(object)
	if IsObjectExists(object) then RemoveObject(object) end
end

function RemoveFactionCreatures(player)
	if MUObjectToRemove == 0 then
		SafeRemoveObject("hav"..player)
		SafeRemoveObject("inf"..player)
		SafeRemoveObject("nec"..player)
		SafeRemoveObject("syl"..player)
		SafeRemoveObject("aca"..player)
		SafeRemoveObject("dun"..player)
		SafeRemoveObject("for"..player)
		SafeRemoveObject("str"..player)
		SafeRemoveObject("neu"..player)
	else
		for i = 1, 4, 1 do
			SafeRemoveObject("mob" .. i .. "_" .. MUObjectToRemove);
		end
	end
end

-- =====================================================================================================================================================
-- SELECTION / BANNING
-- =====================================================================================================================================================


if Mode == 1 then -- selection

	SetObjectPosition("blue" .. 1 .. "_" .. 1, 45, 89)
	SetObjectPosition("blue" .. 1 .. "_" .. 2, 45, 87)
	SetObjectPosition("blue" .. 1 .. "_" .. 3, 45, 85)
	SetObjectPosition("blue" .. 1 .. "_" .. 4, 38, 89)
	SetObjectPosition("blue" .. 1 .. "_" .. 5, 38, 87)
	SetObjectPosition("blue" .. 1 .. "_" .. 6, 38, 85)

	SetObjectPosition("red" .. 2 .. "_" .. 1, 39, 50)
	SetObjectPosition("red" .. 2 .. "_" .. 2, 39, 48)
	SetObjectPosition("red" .. 2 .. "_" .. 3, 39, 46)
	SetObjectPosition("red" .. 2 .. "_" .. 4, 46, 50)
	SetObjectPosition("red" .. 2 .. "_" .. 5, 46, 48)
	SetObjectPosition("red" .. 2 .. "_" .. 6, 46, 46)
	
end

if Mode == 2 then --banning

	SetObjectPosition("blue" .. 2 .. "_" .. 1, 45, 50)
	SetObjectPosition("blue" .. 2 .. "_" .. 2, 45, 48)
	SetObjectPosition("blue" .. 2 .. "_" .. 3, 45, 46)
	SetObjectPosition("blue" .. 2 .. "_" .. 4, 38, 50)
	SetObjectPosition("blue" .. 2 .. "_" .. 5, 38, 48)
	SetObjectPosition("blue" .. 2 .. "_" .. 6, 38, 46)

	SetObjectPosition("red" .. 1 .. "_" .. 1, 39, 89)
	SetObjectPosition("red" .. 1 .. "_" .. 2, 39, 87)
	SetObjectPosition("red" .. 1 .. "_" .. 3, 39, 85)
	SetObjectPosition("red" .. 1 .. "_" .. 4, 46, 89)
	SetObjectPosition("red" .. 1 .. "_" .. 5, 46, 87)
	SetObjectPosition("red" .. 1 .. "_" .. 6, 46, 85)

end

if Mode == 1 or Mode == 2 then

	
	for i=1, 9, 1 do
		Trigger(OBJECT_TOUCH_TRIGGER, ObjectsToBan1[i], "Selection1(" .. i ..")");
		SetObjectEnabled(ObjectsToBan1[i], nil);
	end
	
	for i=1, 9, 1 do
		Trigger(OBJECT_TOUCH_TRIGGER, ObjectsToBan2[i], "Selection2(" .. i ..")");
		SetObjectEnabled(ObjectsToBan2[i], nil);
	end
	
	function Selection1 (number)
		local player = 1;
		local pf = GetPlayerFilter(player)
		if Ban[1] == 0 then
			if Mode == 1 then
				if number == 9 then
					local msg = {
						PATH .. 'Selection.txt';
						color = PATH .. 'c_red.txt',
						race1 = Towns[9],
						race2 = Towns[10]
					}
					QuestionBoxForPlayers(pf, msg, 'FirstBan(' .. number .. ')', 'SelectionNil(' .. 1 .. ')')
				
				end
				if number < 9 then
					local msg = {
						PATH .. 'Selection.txt';
						color = PATH .. 'c_red.txt',
						race1 = Towns[number],
						race2 = Towns[number]
					}
						QuestionBoxForPlayers(pf, msg, 'FirstBan(' .. number .. ')', 'SelectionNil(' .. 1 .. ')')
				end
				
			end
			if Mode == 2 then
				local msg = {
					PATH .. 'Ban.txt';
					color = PATH .. 'c_blue.txt',
					race1 = Towns[number],
					race2 = Towns[number]
				}
				if number == 9 then
					QuestionBoxForPlayers(pf, PATH .. 'No_Ban.txt', 'FirstBan(' .. number .. ')', 'SelectionNil(' .. 1 .. ')')
				else
					QuestionBoxForPlayers(pf, msg, 'FirstBan(' .. number .. ')', 'SelectionNil(' .. 1 .. ')')
				end
			end
		end
	end

	function Selection2 (number)
		local player = 2;
		local pf = GetPlayerFilter(player)
		if Ban[2] == 0 then
			if Mode == 1 then
				local msg = {
					PATH .. 'Selection.txt';
					color = PATH .. 'c_blue.txt',
					race1 = Towns[number],
					race2 = Towns[number]
				}
				if number == 9 then
					local msg = {
						PATH .. 'Selection.txt';
						color = PATH .. 'c_blue.txt',
						race1 = Towns[number],
						race2 = Towns[number+1]
					}
				end
				QuestionBoxForPlayers(pf, msg, 'SecondBan(' .. number .. ')', 'SelectionNil(' .. 2 .. ')')
			end
			if Mode == 2 then
				local msg = {
					PATH .. 'Ban.txt';
					color = PATH .. 'c_red.txt',
					race1 = Towns[number],
					race2 = Towns[number]
				}
				if number == 9 then
					QuestionBoxForPlayers(pf, PATH .. 'No_Ban.txt', 'SecondBan(' .. number .. ')', 'SelectionNil(' .. 2 .. ')')
				else
					QuestionBoxForPlayers(pf, msg, 'SecondBan(' .. number .. ')', 'SelectionNil(' .. 2 .. ')')
				end
			end
		end
	end

	function SelectionNil (number)
		Ban[number] = 0;
	end
	
	function BeginingSign ()
		while GetDate(DAY) == 1 do
			sleep(1)
		end
		if Mode == 1 then
			ShowFlyingSign (PATH.."Choosing_1.txt", Hero0[1], PLAYER_1, 10.0);
			ShowFlyingSign (PATH.."Choosing_1.txt", Hero0[2], PLAYER_2, 10.0);
		end
		if Mode == 2 then
			ShowFlyingSign (PATH.."Banning_1.txt", Hero0[1], PLAYER_1, 10.0);
			ShowFlyingSign (PATH.."Banning_1.txt", Hero0[2], PLAYER_2, 10.0);
		end
	end
	

	function BeginingMP1 (player)
		local i = 0;
		sleep(5)
		if GetDate(DAY) == 1 then
			ShowFlyingSign (PATH.."END_TURN.txt", Hero0[player], player, 3.0);
		end
		while GetDate(DAY) == 1 do
			if i > 45 then
				ShowFlyingSign (PATH.."END_TURN.txt", Hero0[player], player, 3.0);
				i = 0;
			end
			sleep(1)
			i=i+1;
		end
		while InfiniteLoop do
			if Ban[player] > 0 then 
				ChangeHeroStat(Hero0[player], 7, -10000)
				return 0;
			end
			if GetHeroStat(Hero0[player], 7) < 1000 then ChangeHeroStat(Hero0[player], 7, 10000) end
			sleep(3)
		end
	end


	function RemoveMonster (faction, player)
		if player == 1 then
			Trigger(OBJECT_TOUCH_TRIGGER, ObjectsToBan1[faction], nil);
			RemoveObject(ObjectsToBan1[faction]);
		end
		if player == 2 then
			Trigger(OBJECT_TOUCH_TRIGGER, ObjectsToBan2[faction], nil);
			RemoveObject(ObjectsToBan2[faction]);
		end
		if player == 3 then
			sleep(2)
			Trigger(OBJECT_TOUCH_TRIGGER, ObjectsToBan1[faction], nil);
			Trigger(OBJECT_TOUCH_TRIGGER, ObjectsToBan2[faction], nil);
			RemoveObject(ObjectsToBan1[faction]);
			RemoveObject(ObjectsToBan2[faction]);
		end	
	end

	function FirstBan (firBan)
		if Ban[1] == 0 then
			if Mode == 1 then
				if firBan == 9 then firBan = random(8)+1 end
			end
			Ban[1] = firBan;
			GameBegin1 = GameBegin1 + 1;
			startThread(RemoveMonster, firBan, 1)
		end
	end


	function SecondBan (SecBan)
		if Ban[2] == 0 then
			if Mode == 1 then
				if SecBan == 9 then SecBan = random(8)+1 end
			end
			Ban[2] = SecBan;
			GameBegin2 = GameBegin2 + 1;
			startThread(RemoveMonster, SecBan, 2)
		end
	end



end

-- =====================================================================================================================================================
-- MATCHUP
-- =====================================================================================================================================================

MUObjectToRemove = 0;

if Mode == 4 then
	
	NatchupFaction = { 0, 0, 0, 0, 0, 0, 0, 0 }
	
	function MU_Random_Faction (faction, deleted_faction, faction2)
	
		if faction == nil then faction = 0; end 
		if deleted_faction == nil then deleted_faction = 0; end 
		if faction2 == nil then faction2 = 0; end 
		
		
		if deleted_faction > 0 then NatchupFaction[deleted_faction] = NatchupFaction[deleted_faction] - 1; end
		
				
		local rand = random(8)+1; 
		
		
		while NatchupFaction[rand] >= 4 or rand == faction or rand == faction2 do
			rand = random(8)+1; 
			sleep(1)
		end
		
		NatchupFaction[rand] = NatchupFaction[rand] + 1;
		
		return rand;
		
	end
	
	
	MirrorSamePairCout = 1;
	
	MatchupFaction1 = { MU_Random_Faction(0), MU_Random_Faction(0), MU_Random_Faction(0), MU_Random_Faction(0), MU_Random_Faction(0), MU_Random_Faction(0), MU_Random_Faction(0), MU_Random_Faction(0) }
	MatchupFaction2 = {
		MU_Random_Faction(MatchupFaction1[1]),
		MU_Random_Faction(MatchupFaction1[2]),
		MU_Random_Faction(MatchupFaction1[3]),
		MU_Random_Faction(MatchupFaction1[4]),
		MU_Random_Faction(MatchupFaction1[5]),
		MU_Random_Faction(MatchupFaction1[6]),
		MU_Random_Faction(MatchupFaction1[7]),
		MU_Random_Faction(MatchupFaction1[8])
		}	
	
	
	
	
	MU_ban_count = 0;
	

	CreaturesRace = { 6, 20, 36, 50, 62, 76, 99, 122, 88}
	
	RemoveFactionCreatures(1)
	RemoveFactionCreatures(2)
	
	sleep(1)
	
	MU_rand_2 = 0;
	
	for i=1, 8, 1 do 
		while MatchupFaction1[i] == 0 or MatchupFaction2[i] == 0 do
			sleep(1)
		end
	end
	
	MU_rand_1 = 0;
	
	MU_test1 = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
	MU_test2 = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
	MU_test11 = 0;
	MU_test21 = 0;
	
	while MirrorSamePairCout > 0 do
		MirrorSamePairCout = 0;
		for i=1, 8, 1 do
			for i1=1, 8, 1 do
				MU_rand_2 = 0;
				if i == i1 then i1 = i1 + 1 end
				while MatchupFaction1[i] == MatchupFaction2[i]  do 

					MatchupFaction1[i] = MU_Random_Faction(MatchupFaction1[i], MatchupFaction1[i]);
					sleep(1)
					if MU_rand_2 == 5 then
						MU_rand_2 = 0;
						MatchupFaction2[i] = MU_Random_Faction(MatchupFaction1[i], MatchupFaction1[i]);
						sleep(1);
					end
					MU_rand_2 = MU_rand_2 + 1;
					MirrorSamePairCout = MirrorSamePairCout + 1;
				
				end
				MU_rand_1 = 0;
				MU_rand_2 = 0;
				
				
				while (MatchupFaction1[i] == MatchupFaction1[i1] and MatchupFaction2[i] == MatchupFaction2[i1]) or (MatchupFaction1[i] == MatchupFaction2[i1] and MatchupFaction2[i] == MatchupFaction1[i1]) do -- or MU_rand_1 == MatchupFaction1[i1] do

					MatchupFaction1[i1] = MU_Random_Faction(MatchupFaction1[i1], MatchupFaction1[i1], MatchupFaction2[i1]);

					sleep(1)
					if MU_rand_2 == 5 then
						MU_rand_2 = 0;
						MatchupFaction2[i] = MU_Random_Faction(MatchupFaction1[i1], MatchupFaction1[i1], MatchupFaction2[i1]);
						sleep(1);
					end
					MU_rand_2 = MU_rand_2 + 1;

					MirrorSamePairCout = MirrorSamePairCout + 1;
				end
				
				
			end
		end
	end
	

	
	MU_player = 1;
	
	
	
	function MU_ban (number, player)
		if mod(MU_ban_count, 2) == 1 and player == 1 then
			return 0;
		end	
		if mod(MU_ban_count, 2) == 0 and player == 2 then
			return 0;
		end
		MU_ban_count = MU_ban_count + 1;
		if MU_player == 1 then
			MU_player = 2;
			ChangeHeroStat(Hero0[2], 7, -5000)
		elseif MU_player == 2 then
			ChangeHeroStat(Hero0[1], 7, -5000)
			MU_player = 1;
		end

		Trigger(OBJECT_TOUCH_TRIGGER, "mob" .. 1 .. "_" .. number, nil);
		Trigger(OBJECT_TOUCH_TRIGGER, "mob" .. 2 .. "_" .. number, nil);
		RemoveObject("mob" .. 1 .. "_" .. number)
		RemoveObject("mob" .. 2 .. "_" .. number)
		RemoveObject("mob" .. 3 .. "_" .. number)
		RemoveObject("mob" .. 4  .. "_" .. number)
		MatchupFaction1[number] = 0;
		if MU_ban_count == 6 then
			local MU_last = 0;
			for i=1, 8, 1 do
				if MatchupFaction1[i] > 0 and MU_last == 0 then
					MU_last = i;
				elseif MatchupFaction1[i] > 0 and MU_last > 0 then
					local rand = random(2)+1;

					sleep(3)
					if rand == 1 then
						HeroRace[1] = MatchupFaction1[i]
						HeroRace[2] = MatchupFaction2[i]
						Trigger(OBJECT_TOUCH_TRIGGER, "mob" .. 1 .. "_" .. MU_last, nil);
						Trigger(OBJECT_TOUCH_TRIGGER, "mob" .. 2 .. "_" .. MU_last, nil);
						RemoveObject("mob" .. 1 .. "_" .. MU_last)
						RemoveObject("mob" .. 2 .. "_" .. MU_last)
						RemoveObject("mob" .. 3 .. "_" .. MU_last)
						RemoveObject("mob" .. 4  .. "_" .. MU_last)
						GameBegin1 = 1;
						MUObjectToRemove = i;
					end
					if rand == 2 then 
						HeroRace[1] = MatchupFaction1[MU_last]
						HeroRace[2] = MatchupFaction2[MU_last]
						Trigger(OBJECT_TOUCH_TRIGGER, "mob" .. 1 .. "_" .. i, nil);
						Trigger(OBJECT_TOUCH_TRIGGER, "mob" .. 2 .. "_" .. i, nil);
						RemoveObject("mob" .. 1 .. "_" .. i)
						RemoveObject("mob" .. 2 .. "_" .. i)
						RemoveObject("mob" .. 3 .. "_" .. i)
						RemoveObject("mob" .. 4  .. "_" .. i)
						GameBegin1 = 1;
						MUObjectToRemove = MU_last;
					end
				end
			end
		end
	end
	
	function MU_begin (x)
		sleep(6)
		if MU_ban_count < 6 then
			ShowFlyingSign (PATH.."END_TURN.txt", Hero0[x], x, 3.0);
		end
	end
	
	function MU_Movement ()
		if GetDate(DAY) == 1 then
			startThread(MU_begin, 1)
			startThread(MU_begin, 2)
			sleep(1)
		end
		while GetDate(DAY) == 1 do

			sleep(1)
		end
		ChangeHeroStat(Hero0[1], 7, -5000)
		sleep(10)
		while MU_ban_count < 6 do
			if MU_player == 1 then
				ChangeHeroStat(Hero0[1], 7, 5000)
				ChangeHeroStat(Hero0[2], 7, -5000)
			end
			if MU_player == 2 then
				ChangeHeroStat(Hero0[2], 7, 5000)
				ChangeHeroStat(Hero0[1], 7, -5000)
			end
			sleep(1)
		end
	end

	
	function MU_FlyingSign ()
		while GetDate(DAY) == 1 do
			sleep(1)
		end
		local MU_FlyingSign_player = 1
		while MU_ban_count < 6 do 
			if MU_FlyingSign_player == MU_player then
				if MU_player == 1 then
					ShowFlyingSign (PATH.."MU_1.txt", Hero0[1], PLAYER_1, 10.0);
					MU_FlyingSign_player = 2;
				end
				if MU_player == 2 then
					ShowFlyingSign (PATH.."MU_1.txt", Hero0[2], PLAYER_2, 10.0);
					MU_FlyingSign_player = 1;
				end
			end
			sleep(1)
		end
	end
	

	function CreateMonsterMU (number, x, y)

		local name1 = "mob" .. 1 .. "_" .. number;
		local name2 = "mob" .. 2 .. "_" .. number;
		local name3 = "mob" .. 3 .. "_" .. number;
		local name4 = "mob" .. 4 .. "_" .. number;

		CreateMonster(name1, CreaturesRace[MatchupFaction2[number]], 1, x + 1, y, 1, MONSTER_MOOD_FRIENDLY, MONSTER_COURAGE_ALWAYS_JOIN, -90)
		CreateMonster(name2, CreaturesRace[MatchupFaction1[number]], 1, x, y, 1, MONSTER_MOOD_FRIENDLY, MONSTER_COURAGE_ALWAYS_JOIN, 90)
		CreateMonster(name3, CreaturesRace[MatchupFaction2[number]], 1, x + 1, y + 39, 1, MONSTER_MOOD_FRIENDLY, MONSTER_COURAGE_ALWAYS_JOIN, -90)
		CreateMonster(name4, CreaturesRace[MatchupFaction1[number]], 1, x, y + 39, 1, MONSTER_MOOD_FRIENDLY, MONSTER_COURAGE_ALWAYS_JOIN, 90)
	end

	function MoveMonsterMU (number, x, y)
		local name1 = "mob" .. 1 .. "_" .. number;
		local name2 = "mob" .. 2 .. "_" .. number;
		local name3 = "mob" .. 3 .. "_" .. number;
		local name4 = "mob" .. 4 .. "_" .. number;

		SetObjectPosition(name1, x + 1, y, 0)
		SetObjectPosition(name2, x, y, 0)
		SetObjectPosition(name3, x + 1, y + 39, 0)
		SetObjectPosition(name4, x , y + 39, 0)

		
		SetObjectEnabled(name1, nil);
		SetObjectEnabled(name2, nil);
		SetObjectEnabled(name3, nil);
		SetObjectEnabled(name4, nil);

		if number < 5 then
			Trigger(OBJECT_TOUCH_TRIGGER, name1, 'MUQuestion(' .. number .. ', ' .. 1 .. ')');
			Trigger(OBJECT_TOUCH_TRIGGER, name3, 'MUQuestion(' .. number .. ', ' .. 2 .. ')');
		end
		if number > 4 then
			Trigger(OBJECT_TOUCH_TRIGGER, name2, 'MUQuestion(' .. number .. ', ' .. 1 .. ')');
			Trigger(OBJECT_TOUCH_TRIGGER, name4, 'MUQuestion(' .. number .. ', ' .. 2 .. ')');
		end

		SetMonsterNames(name1, MONSTER_NAMES_ALL, Towns[MatchupFaction2[number]])
		SetMonsterNames(name2, MONSTER_NAMES_ALL, Towns[MatchupFaction1[number]])
		SetMonsterNames(name3, MONSTER_NAMES_ALL, Towns[MatchupFaction2[number]])
		SetMonsterNames(name4, MONSTER_NAMES_ALL, Towns[MatchupFaction1[number]])
	end


	CreateMonsterMU(1, 40, 51)
	CreateMonsterMU(2, 40, 49)
	CreateMonsterMU(3, 40, 47)
	CreateMonsterMU(4, 40, 45)
	CreateMonsterMU(5, 45, 51)
	CreateMonsterMU(6, 45, 49)
	CreateMonsterMU(7, 45, 47)
	CreateMonsterMU(8, 45, 45)

	sleep(1);

	MoveMonsterMU(1, 38, 51)
	MoveMonsterMU(2, 38, 49)
	MoveMonsterMU(3, 38, 47)
	MoveMonsterMU(4, 38, 45)
	MoveMonsterMU(5, 45, 51)
	MoveMonsterMU(6, 45, 49)
	MoveMonsterMU(7, 45, 47)
	MoveMonsterMU(8, 45, 45)
	

	function MUQuestion(deleted_matchup, player)
		if MU_ban_count == 1 or MU_ban_count == 3 or MU_ban_count == 5 and player == 1 then
			return 0;
		end
		if MU_ban_count == 2 or MU_ban_count == 4 or MU_ban_count == 6 and player == 2 then
			return 0;
		end

		local lcolor, rcolor = PATH .. 'c_red.txt', PATH .. 'c_blue.txt'

		local msg = {
			PATH .. 'QuestionMatchupE.txt';
			lcolor = lcolor,
			rcolor = rcolor,
			lrace = Towns[MatchupFaction1[deleted_matchup]],
			rrace = Towns[MatchupFaction2[deleted_matchup]],
		}
		QuestionBoxForPlayers(GetPlayerFilter(player), msg, 'MU_ban(' .. deleted_matchup .. ', ' .. player .. ')--', '')
	end

	startThread(MU_Movement)
	startThread(MU_FlyingSign)

end

--=======================================================================
--=======================================================================
--=======================================================================


if Mode == 1 then
	sleep(5)
	startThread(BeginingMP1, 1)
	startThread(BeginingMP1, 2)
	startThread(BeginingSign)
end
if Mode == 2 then
	sleep(5)
	startThread(BeginingMP1, 1)
	startThread(BeginingMP1, 2)
	startThread(BeginingSign)
end


if Mode == 1 or Mode == 2 then
	while GameBegin1 < 1 do	
		sleep(1);
	end
	while GameBegin2 < 1 do
		sleep(1);
	end
end


if Mode == 4 then
	while GameBegin1 < 1 do
		sleep(1);
	end
end

NotMirrorMatchup = 1

HeroBansEnd = 0;

if Mode == 1 then
	HeroRace = { Ban[1], Ban[2] }
	if Ban[1] == Ban[2] then
		NotMirrorMatchup = nil
		HeroBansEnd = 1
	end
end




if Mode == 2 then
	HeroRace = { RandomClock(8)+1, RandomClock(8)+1 }
	while HeroRace[1] == Ban[1] or HeroRace[1] == Ban[2] do	
		HeroRace[1] = RandomClock(8)+1;
	end
	while HeroRace[2] == Ban[1] or HeroRace[2] == Ban[2] or HeroRace[2] == HeroRace[1] do	
		HeroRace[2] = RandomClock(8)+1;
	end
end


if Mode == 3 then
	HeroRace = { RandomClock(8)+1, RandomClock(8)+1 }
	while HeroRace[1] == HeroRace[2] do
		HeroRace[2] = RandomClock(8)+1;
	end
end

function DisplaceAllCrystals(crystal, c)
	local obj;
	for p = 1, 2, 1 do
		local py = (p - 1) * 39;
		SafeRemoveObject(crystal .. p .. "_1");
		-- for i = 1, 6, 1 do
		-- 	obj = crystal .. p .. "_" .. i;
		-- 	SafeRemoveObject(obj);
		-- end
		for i = 2, 6, 1 do
			obj = crystal .. p .. "_" .. i;
			SetObjectPosition(obj, 34 + (i * 2), 44 + c + py, 0)
		end
	end 
end
DisplaceAllCrystals("blue", 8)
DisplaceAllCrystals("red", 0)
RemoveFactionCreatures(1)
RemoveFactionCreatures(2)


HeroesChoosing = {
	{{0, 0, 0}, {0, 0, 0}, {0, 0, 0}},
	{{0, 0, 0}, {0, 0, 0}, {0, 0, 0}}
}

function GenerateHeroes(player)
	local faction = HeroRace[player];
	local heroes = HEROES[faction];
	for i1 = 1, 3, 1 do
		for i2 = 1, 3, 1 do
			HeroesChoosing[player][i1][i2] = RandElementRemove(heroes);	
		end
	end
end

function HeroBanningInit(player)	
	local p = (player - 1) * 39;

	SetObjectPosition(Hero0[player], 42, 48 + p, 0)

	SetObjectPosition(HeroesChoosing[2][1][1].ico..player, 38, 50 + p, 0);
	SetObjectPosition(HeroesChoosing[2][1][2].ico..player, 38, 51 + p, 0);
	SetObjectPosition(HeroesChoosing[2][1][3].ico..player, 39, 51 + p, 0);

	SetObjectPosition(HeroesChoosing[2][2][1].ico..player, 41, 51 + p, 0);
	SetObjectPosition(HeroesChoosing[2][2][2].ico..player, 42, 51 + p, 0);
	SetObjectPosition(HeroesChoosing[2][2][3].ico..player, 43, 51 + p, 0);

	SetObjectPosition(HeroesChoosing[2][3][1].ico..player, 45, 51 + p, 0);
	SetObjectPosition(HeroesChoosing[2][3][2].ico..player, 46, 51 + p, 0);
	SetObjectPosition(HeroesChoosing[2][3][3].ico..player, 46, 50 + p, 0);


	SetObjectPosition(HeroesChoosing[1][1][1].ico..player, 38, 46 + p, 0);
	SetObjectPosition(HeroesChoosing[1][1][2].ico..player, 38, 45 + p, 0);
	SetObjectPosition(HeroesChoosing[1][1][3].ico..player, 39, 45 + p, 0);

	SetObjectPosition(HeroesChoosing[1][2][1].ico..player, 41, 45 + p, 0);
	SetObjectPosition(HeroesChoosing[1][2][2].ico..player, 42, 45 + p, 0);
	SetObjectPosition(HeroesChoosing[1][2][3].ico..player, 43, 45 + p, 0);

	SetObjectPosition(HeroesChoosing[1][3][1].ico..player, 45, 45 + p, 0);
	SetObjectPosition(HeroesChoosing[1][3][2].ico..player, 46, 45 + p, 0);
	SetObjectPosition(HeroesChoosing[1][3][3].ico..player, 46, 46 + p, 0);

	for n = 1, 2, 1 do
		for c = 1, 3, 1 do
			for h = 1, 3, 1 do
				Trigger(OBJECT_TOUCH_TRIGGER, HeroesChoosing[n][c][h].ico..player, "BanHeroes("..player..","..n..","..c..")")
				SetObjectEnabled(HeroesChoosing[n][c][h].ico..player, nil);
			end
		end
	end
end

HeroBans = {2, 1, 2, 1}
HeroBansCount = 0;

HeroBansB = {
	{1, 1, 1},
	{1, 1, 1}
}

function BanHeroes(player, playerHeroes, heroes)
	if HeroBans[HeroBansCount+1] ~= nil then	
		if HeroBans[HeroBansCount+1] == player then	
			HeroBansCount = HeroBansCount + 1;
			if (HeroBansB[playerHeroes][1] + HeroBansB[playerHeroes][2] + HeroBansB[playerHeroes][3]) < 2 then
				MessageBoxForPlayers(GetPlayerFilter(player), PATH.."banHeroesNo.txt");
				HeroBansCount = HeroBansCount - 1;
				return
			end
			QuestionBoxForPlayers(GetPlayerFilter(player), PATH.."banHeroesQuestion.txt", "BanHeroesYes("..player..","..playerHeroes..","..heroes..")", "BanHeroesNo")
			return
		end
	end
end

function BanHeroesYes(player, playerHeroes, heroes)
	if HeroBans[HeroBansCount] == player then
		if (HeroBansB[playerHeroes][1] + HeroBansB[playerHeroes][2] + HeroBansB[playerHeroes][3]) < 2 then
			return
		end
		for p = 1, 2, 1 do
			for i = 1, 3, 1 do
				RemoveObject(HeroesChoosing[playerHeroes][heroes][i].ico..p)
			end
		end
		HeroBansB[playerHeroes][heroes] = 0;
		if (HeroBansB[1][1] + HeroBansB[1][2] + HeroBansB[1][3] + HeroBansB[2][1] + HeroBansB[2][2] + HeroBansB[2][3]) == 2 then
			HeroBansEnd = 1;
		else
			HeroBanningMesssageMovement()
		end
		return
	end
end

function BanHeroesNo()
	HeroBansCount = HeroBansCount - 1;
end


function MovementLoop0(hero, player)
	while IsObjectExists(hero) do
		ChangeHeroStat(hero, 7, MovementAdd[player]);
		sleep()
	end
end

startThread(MovementLoop0, Hero0[1], 1);
startThread(MovementLoop0, Hero0[2], 2);

function HeroBanningMesssageMovement()
	local c = HeroBans[HeroBansCount+1];
	local o = Opponent(c)
	ChangeHeroStat(Hero0[o], 7, -10000)
	MovementAdd[o] = -10000;

	ChangeHeroStat(Hero0[c], 7, 10000)
	MovementAdd[c] = 10000;


	ShowFlyingSign(PATH.."banHeroesWait.txt", Hero0[o], o, 5.0);
	ShowFlyingSign(PATH.."banHeroesBan.txt", Hero0[c], c, 5.0);
end

if Mode == 3 then
	ShowFlyingSign (PATH.."END_TURN.txt", Hero0[1], 1, 3.0);
	ShowFlyingSign (PATH.."END_TURN.txt", Hero0[2], 2, 3.0);
	while GetDate(DAY) == 1 do
		sleep()
	end
end

if NotMirrorMatchup then

	GenerateHeroes(1);
	GenerateHeroes(2);
	
	HeroBanningInit(1)
	HeroBanningInit(2)

	HeroBanningMesssageMovement()
end



while HeroBansEnd == 0 do
	sleep()
end

sleep(1)

function DeployHeroes()
	local h1 = {};
	local h2 = {}
	local hero1, hero2, rHero1, rHero2;
	local cIndex = {0, 0};
	for i = 1, 3, 1 do
		if HeroBansB[1][i] == 1 then
			cIndex[1] = i;
			for n = 1, 3, 1 do
				h1[n] = HeroesChoosing[1][i][n].name;
			end
		end
		if HeroBansB[2][i] == 1 then
			cIndex[2] = i;
			for n = 1, 3, 1 do
				h2[n] = HeroesChoosing[2][i][n].name;
			end
		end
	end
	hero1 = RandElementRemove(h1);
	hero2 = RandElementRemove(h2);
	if hero1 == hero2 then
		hero2 = RandElementRemove(h2);
	end
	-- rHero1 = hero1;
	local heroes = {hero1, hero2}

	hero2 = hero2.."2";
	DeployReserveHero(hero1, 44, 41, 0)
	DeployReserveHero(hero2, 35, 85, 0)
	Hero1 = { hero1, hero2 }
	for i = 1, 3, 1 do
		for p = 1, 2, 1 do
			if HeroesChoosing[p][cIndex[p]][i].name == heroes[p] then
				if p == 1 then
					SafeRemoveObject(HeroesChoosing[p][cIndex[p]][i].ico..2)
					SetObjectPosition(HeroesChoosing[p][cIndex[p]][i].ico..1, 31, 88, 0);
				elseif p == 2 then
					SafeRemoveObject(HeroesChoosing[p][cIndex[p]][i].ico..1)
					SetObjectPosition(HeroesChoosing[p][cIndex[p]][i].ico..2, 46, 36, 0);
				end
			else
				for pl = 1, 2, 1 do
					SafeRemoveObject(HeroesChoosing[p][cIndex[p]][i].ico..pl)
				end
			end	
		end
	end
end

function MirrorDeployHeroes()
	local rand1 = RandElementRemove(HEROES[HeroRace[1]]);
	local rand2 = RandElementRemove(HEROES[HeroRace[2]]);

	SetObjectPosition(rand1.ico..1, 31, 88, 0);
	SetObjectPosition(rand2.ico..2, 46, 36, 0);
	rand1 = rand1.name
	rand2 = rand2.name
	DeployReserveHero(rand1, 44, 41, 0)
	DeployReserveHero(rand2 .. "2" , 35, 85, 0)
	Hero1 = { rand1, rand2 .. "2", rand2 }
end

if NotMirrorMatchup then
	DeployHeroes();
else
	MirrorDeployHeroes()
end

GlobalClockWork = 1;




ChangeHeroStat(Hero1[1], 7, -GetHeroStat(Hero1[1], 7))
ChangeHeroStat(Hero1[2], 7, -GetHeroStat(Hero1[2], 7))



function Transform_Town (town, player)
  if HeroRace[player] == 1 then TransformTown(town, 0) end
  if HeroRace[player] == 2 then TransformTown(town, 5) end
  if HeroRace[player] == 3 then TransformTown(town, 4) end
  if HeroRace[player] == 4 then TransformTown(town, 1) end
  if HeroRace[player] == 5 then TransformTown(town, 2) end
  if HeroRace[player] == 6 then TransformTown(town, 3) end
  if HeroRace[player] == 7 then TransformTown(town, 6) end
  if HeroRace[player] == 8 then TransformTown(town, 7) end
end


Transform_Town(Town[1], 1)
Transform_Town(Town[2], 2)



RemoveObject(Hero0[1]);--Hangvul, choosing1, choosing2
RemoveObject(Hero0[2]);


function Replace_Dwelling (dwelling, player)
  if HeroRace[player] == 1 then ReplaceDwelling(dwelling, 0) end
  if HeroRace[player] == 2 then ReplaceDwelling(dwelling, 5) end
  if HeroRace[player] == 3 then ReplaceDwelling(dwelling, 4) end
  if HeroRace[player] == 4 then ReplaceDwelling(dwelling, 1) end
  if HeroRace[player] == 5 then ReplaceDwelling(dwelling, 2) end
  if HeroRace[player] == 6 then ReplaceDwelling(dwelling, 3) end
  if HeroRace[player] == 7 then ReplaceDwelling(dwelling, 6) end
  if HeroRace[player] == 8 then ReplaceDwelling(dwelling, 7) end
end

Replace_Dwelling("enemy_1", 2);
Replace_Dwelling("enemy_2", 1);

SetObjectEnabled("enemy_1", nil);
SetObjectEnabled("enemy_2", nil);

function DwellingName (faction, player)
	local dwelling = Opponent(player);
	-- OverrideObjectTooltipNameAndDescription("enemy_" .. dwelling, Towns[HeroRace[player]], "/Text/Game/Heroes/Persons/" .. faction .. "/" .. Hero1[player] .. "/Name.txt")
	OverrideObjectTooltipNameAndDescription("enemy_" .. dwelling, Towns[HeroRace[player]], Towns[HeroRace[player]])
end

function DwellingsInit(player)
	local race = HeroRace[player];
	if race == 1 then DwellingName ("Haven", player)
	elseif race == 2 then DwellingName ("Inferno", player)
	elseif race == 3 then DwellingName ("Necropolis", player)
	elseif race == 4 then DwellingName ("Preserve", player)
	elseif race == 5 then DwellingName ("Academy", player)
	elseif race == 6 then DwellingName ("Dungeon", player)
	elseif race == 7 then DwellingName ("Dwarves", player)
	elseif race == 8 then DwellingName ("Stronghold", player) end
end

DwellingsInit(1)
DwellingsInit(2)

-- =====================================================================================================================================================
-- BUILDINGS
-- =====================================================================================================================================================

function Guild (town_name, player)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_MAGIC_GUILD)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_MAGIC_GUILD)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_MAGIC_GUILD)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_MAGIC_GUILD)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_MAGIC_GUILD)
	if HeroRace[player] == 5 then --aca
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_SPECIAL_4, 0, 0)
	end
	if HeroRace[player] == 8 then --str
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)	
	end
end	

function TownBuildings (town_name, player)
	DestroyTownBuildingToLevel("sylvanTown" .. player, TOWN_BUILDING_TOWN_HALL, 0, 0);
	DestroyTownBuildingToLevel("academyTown" .. player, TOWN_BUILDING_TOWN_HALL, 0, 0);

	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_1)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_1)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_2)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_2)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_3)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_3)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_4)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_4)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_5)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_5)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_6)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_6)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_7)
	UpgradeTownBuilding (town_name, TOWN_BUILDING_DWELLING_7)

	DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_TAVERN, 0, 0)
	DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_BLACKSMITH, 0, 0)
	DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_TOWN_HALL, 0, 0)
	DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_MARKETPLACE, 0, 0)
	DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_FORT, 0, 0)


	if HeroRace[player] == 1 then --hav
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_2)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_4)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_5)
	end

	if HeroRace[player] == 2 then --inf
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_2)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_4)
		DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_SPECIAL_1, 0, 0)
	end

	if HeroRace[player] == 3 then --necr
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_2)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_3)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_4)
		
		--DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_SPECIAL_2, 0, 0)
	end

	if HeroRace[player] == 4 then --sylv
		--UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_0) -- Avengers Guild
		--UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_2)
		--UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_2) -- pond
		DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_SPECIAL_2, 0, 0)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_4)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_5)
		DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_SPECIAL_0, 0, 0)
	end

	if HeroRace[player] == 5 then --aca
		--UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		--UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_2) --artifact forge
		DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_SPECIAL_2, 0, 0)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_3)
		DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_SPECIAL_4, 0, 0)
	end

	if HeroRace[player] == 6 then --dung
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_SPECIAL_3, 0, 0)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_4)
		--UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_6) -- +1 kn
		DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_SPECIAL_6, 0, 0)
		DestroyTownBuildingToLevel(town_name, TOWN_BUILDING_SPECIAL_1, 1, 0)
	end

	if HeroRace[player] == 7 then --for
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_2)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_3)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_5)	
	end

	if HeroRace[player] == 8 then --str
		--UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		--UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		--UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_1)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_2)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_3)
		UpgradeTownBuilding (town_name, TOWN_BUILDING_SPECIAL_5)	

	end
	sleep(1);
	SetNilCreaturesAll();
end

sleep(1)

Guild(Town[1], 1)
Guild(Town[2], 2)



--CreateMonster( monsterName, creatureType, creaturesCount, x, y, floorID, mood= MONSTER_MOOD_AGGRESSIVE, courage= MONSTER_COURAGE_CAN_FLEE_JOIN, rotation= 0 );

sleep(1)

function SetNilCreatures (town, c1, c2, c3, c4, c5, c6, c7)
	SetObjectDwellingCreatures(town, c1, 0);
	SetObjectDwellingCreatures(town, c2, 0);
	SetObjectDwellingCreatures(town, c3, 0);
	SetObjectDwellingCreatures(town, c4, 0);
	SetObjectDwellingCreatures(town, c5, 0);
	SetObjectDwellingCreatures(town, c6, 0);
	SetObjectDwellingCreatures(town, c7, 0);
end

function SetNilCreaturesAll ()
	startThread(SetNilCreaturesTowns, Town[1],  HeroRace[1]);
	startThread(SetNilCreaturesTowns, Town[2],  HeroRace[2]);
end

function SetNilCreaturesTowns (town, race)
	if race == 1 then SetNilCreatures(town, 1, 3, 5, 7, 9, 11, 13);
	elseif race == 2 then SetNilCreatures(town, 15, 17, 19, 21, 23, 25, 27);
	elseif race == 3 then SetNilCreatures(town, 29, 31, 33, 35, 37, 39, 41);
	elseif race == 4 then SetNilCreatures(town, 43, 45, 47, 49, 51, 53, 55);
	elseif race == 5 then SetNilCreatures(town, 57, 59, 61, 63, 65, 67, 69);
	elseif race == 6 then SetNilCreatures(town, 71, 73, 75, 77, 79, 81, 83);
	elseif race == 7 then SetNilCreatures(town, 92, 94, 96, 98, 100, 102, 104);
	elseif race == 8 then SetNilCreatures(town, 117, 119, 121, 123, 125, 127, 129); end
end

function SetTownCreatures2 (town, c1, c2, c3, c4, c5, c6, c7, i1, i2, i3, i4, i5, i6, i7)
	SetObjectDwellingCreatures(town, c1, i1);
	SetObjectDwellingCreatures(town, c2, i2);
	SetObjectDwellingCreatures(town, c3, i3);
	SetObjectDwellingCreatures(town, c4, i4);
	SetObjectDwellingCreatures(town, c5, i5);
	SetObjectDwellingCreatures(town, c6, i6);
	SetObjectDwellingCreatures(town, c7, i7);
end

function SetTownCreatures(player)
	local town = Town[player];
	local race = HeroRace[player];

	if race == 1 then SetTownCreatures2(town, 1, 3, 5, 7, 9, 11, 13, 22, 12, 10, 5, 3, 2, 1);
	elseif race == 2 then SetTownCreatures2(town, 15, 17, 19, 21, 23, 25, 27, 16, 15, 8, 5, 3, 2, 1);
	elseif race == 3 then SetTownCreatures2(town, 29, 31, 33, 35, 37, 39, 41, 20, 15, 9, 5, 3, 2, 1);
	elseif race == 4 then SetTownCreatures2(town, 43, 45, 47, 49, 51, 53, 55, 10, 9, 7, 4, 3, 2, 1);
	elseif race == 5 then SetTownCreatures2(town, 57, 59, 61, 63, 65, 67, 69, 20, 14, 9, 5, 3, 2, 1);
	elseif race == 6 then SetTownCreatures2(town, 71, 73, 75, 77, 79, 81, 83, 7, 5, 6, 4, 3, 2, 1);
	elseif race == 7 then SetTownCreatures2(town, 92, 94, 96, 98, 100, 102, 104, 18, 14, 7, 6, 3, 2, 1);
	elseif race == 8 then SetTownCreatures2(town, 117, 119, 121, 123, 125, 127, 129, 25, 14, 11, 5, 5, 2, 1); end
end


-- =====================================================================================================================================================
-- SPELLS CHECK
-- =====================================================================================================================================================

function Get_Spells (hero, hero2, id, spells_min, spells_max)
	local i=spells_min;
	local i1=1;
	local spell;
	while i <= spells_max do
		local hasspell = 0;

		while i1 <= SpellsAmmount[i] do
			spell = SPELLS[i][i1]["id"];
			if KnowHeroSpell(hero, spell) ~= nil or KnowHeroSpell(hero2, spell) ~= nil then
				hasspell = 1;
			end	
			HeroSpells[id][i][i1] = hasspell;
			hasspell = 0;
			i1=i1+1;
		end
		i=i+1;
		i1=1;
	end
end

function GetSpellsHero(player)
	local town = Town[player];
	SetObjectOwner(town, 8)
	local stronghold = 0;
	if HeroRace[player] == 8 then stronghold = 2 end
	local hero = HEROES[FACTION_SPECIAL][player+stronghold].name;
	if player == 1 then
		DeployReserveHero(hero, 56, 43, GROUND);
	elseif player == 2 then
		DeployReserveHero(hero, 67, 39, GROUND);
	end
	sleep(1)
	
	MakeHeroInteractWithObject(hero, town);
	sleep(1)

	if IsObjectExists(hero) == 1 then
		RemoveObject(hero)
	end

	if stronghold == 2 then
		Get_Spells(hero, Hero1[player], player, 5, 5)
	else
		Get_Spells(hero, Hero1[player], player, 0, 4) 
	end

	SetObjectOwner(town, 0);
end


GetSpellsHero(1)
GetSpellsHero(2)







-- =====================================================================================================================================================
-- NO FOG
-- =====================================================================================================================================================

function OpenFogUnderound(p1, p2)
	if p1 == 1 then
		OpenCircleFog(91, 30, 1, 20, p2);
		OpenCircleFog(86, 30, 1, 20, p2);
		OpenCircleFog(81, 30, 1, 20, p2);
		OpenCircleFog(76, 30, 1, 20, p2);
		OpenCircleFog(71, 30, 1, 20, p2);
		OpenCircleFog(66, 30, 1, 20, p2);
		OpenCircleFog(56, 30, 1, 15, p2);
		OpenCircleFog(50, 30, 1, 15, p2);
	else
		OpenCircleFog(92, 102, 1, 20, p2);
		OpenCircleFog(87, 102, 1, 20, p2);
		OpenCircleFog(82, 102, 1, 20, p2);
		OpenCircleFog(77, 102, 1, 20, p2);
		OpenCircleFog(72, 102, 1, 20, p2);
		OpenCircleFog(67, 102, 1, 20, p2);
		OpenCircleFog(62, 102, 1, 20, p2);
		OpenCircleFog(57, 102, 1, 15, p2);
		OpenCircleFog(52, 102, 1, 15, p2);
		OpenCircleFog(47, 102, 1, 15, p2);
	
	end
end

function OpenFog1()
	for player = 1, 2, 1 do
		-- cricket funny things
		OpenCircleFog(7, 46, 0, 12, player);
		OpenCircleFog(12, 46, 0, 12, player);
		OpenCircleFog(17, 46, 0, 12, player);
		OpenCircleFog(20, 46, 0, 12, player);

		OpenCircleFog(22, 72, 0, 12, player);
		OpenCircleFog(22, 67, 0, 13, player);

		-- underground
		OpenFogUnderound(player, player)
	end

	-- player1
	-- opponent
	OpenCircleFog(39, 88, 0, 12, PLAYER_1);


	-- town
	OpenCircleFog(95, 34, 0, 15, PLAYER_1)
	OpenCircleFog(95, 43, 0, 15, PLAYER_1)
	OpenCircleFog(95, 53, 0, 15, PLAYER_1)
	OpenCircleFog(95, 63, 0, 15, PLAYER_1)

	-- garrison
	OpenCircleFog(59, 35, 0, 10, PLAYER_1)

	-- necro
	if HeroRace[1] == 3 then
		OpenCircleFog(78, 36, 0, 8, PLAYER_1)
		OpenCircleFog(78, 41, 0, 8, PLAYER_1)
		OpenCircleFog(78, 46, 0, 8, PLAYER_1)
	end

	-- sylvan
	if HeroRace[1] == 4 then
		OpenCircleFog(87, 16, 0, 15, PLAYER_1)
	end

	-- aca
	if HeroRace[1] == 5 then
		OpenCircleFog(49, 12, 0, 15, PLAYER_1)
		OpenCircleFog(53, 12, 0, 15, PLAYER_1)
		OpenCircleFog(57, 12, 0, 15, PLAYER_1)
		OpenCircleFog(49, 16, 0, 15, PLAYER_1)
	end

	-- player2
	-- garrison
	OpenCircleFog(50, 66, 0, 15, PLAYER_2)
	OpenCircleFog(40, 73, 0, 15, PLAYER_2)

	--town
	OpenCircleFog(96, 90, 0, 15, PLAYER_2)
	OpenCircleFog(81, 90, 0, 15, PLAYER_2)
	OpenCircleFog(106, 90, 0, 5, PLAYER_2)

	OpenCircleFog(96, 85, 0, 15, PLAYER_2)
	OpenCircleFog(96, 80, 0, 12, PLAYER_2)
	OpenCircleFog(96, 75, 0, 12, PLAYER_2)
	OpenCircleFog(96, 69, 0, 12, PLAYER_2)


	--nekro
	if HeroRace[2] == 3 then
		OpenCircleFog(68, 89, 0, 14, PLAYER_2)
	end

	--sylvan
	if HeroRace[2] == 4 then
		OpenCircleFog(97, 121, 0, 16, PLAYER_2)
	end
	
	--aca
	if HeroRace[2] == 5 then
		OpenCircleFog(53, 107, 0, 10, PLAYER_2)
		OpenCircleFog(53, 102, 0, 10, PLAYER_2)
		OpenCircleFog(53, 97, 0, 10, PLAYER_2)
		OpenCircleFog(53, 92, 0, 10, PLAYER_2)
		OpenCircleFog(53, 87, 0, 10, PLAYER_2)
		OpenCircleFog(53, 82, 0, 10, PLAYER_2)
	end

	--opponent
	OpenCircleFog(42, 45, 0, 15, PLAYER_2)
end

function OpenFog2()
	for player = 1, 2, 1 do
		OpenCircleFog(59, 37, 0, 10, player)
		OpenCircleFog(59, 42, 0, 10, player)
		OpenCircleFog(59, 47, 0, 10, player)
		OpenCircleFog(59, 52, 0, 10, player)
		OpenCircleFog(59, 57, 0, 10, player)
		OpenCircleFog(59, 62, 0, 10, player)
		OpenCircleFog(59, 67, 0, 10, player)
		
		OpenCircleFog(50, 66, 0, 15, player)
		OpenCircleFog(40, 73, 0, 15, player)
	end
end

function ScoutingOpenFog(player)
	OpenCircleFog(64, 68, 0, 43, player)
	OpenCircleFog(64, 58, 0, 43, player)
	
	OpenFogUnderound(Opponent(player), player)
end

-- print("FOG - COMPLETE");


-- =====================================================================================================================================================
-- RESOURCES
-- =====================================================================================================================================================

function SetPlayerResources(player)

	local race = HeroRace[player];


	SetPlayerResource(player,    GOLD,    Golds[race]);
	SetPlayerResource(player,    WOOD,    Woods[race]);
	SetPlayerResource(player,     ORE,     Ores[race]);
	SetPlayerResource(player, MERCURY, Mercurys[race]);
	SetPlayerResource(player, CRYSTAL, Crystals[race]);
	SetPlayerResource(player,  SULFUR,  Sulfurs[race]);
	SetPlayerResource(player,     GEM,     Gems[race]);

end

SetPlayerResources(PLAYER_1);
SetPlayerResources(PLAYER_2);

-- =====================================================================================================================================================
-- REGIONS BLOCED
-- =====================================================================================================================================================

SetRegionBlocked("start_region1", true, PLAYER_1);--strefa startowa
SetRegionBlocked("start_region2", true, PLAYER_2);
SetRegionBlocked("underground_teleport1", true, PLAYER_1);--po zejĹ›ciu do podziemi
SetRegionBlocked("underground_teleport2", true, PLAYER_2);
SetRegionBlocked("town_portal1", true, PLAYER_1);--przed miastem
SetRegionBlocked("town_portal2", true, PLAYER_2);
SetRegionBlocked("garrison1", true, PLAYER_1);--przed garnizonem
SetRegionBlocked("garrison2", true, PLAYER_2);

SetObjectEnabled("garrison_2", nil)

--print("REGIONS BLOCED - COMPLETE");

-- =====================================================================================================================================================
-- CREATURES
-- =====================================================================================================================================================

function ReplaceCreatures(hero, creature1, creature2)
	if GetHeroCreatures(hero, creature1) > 0 then
		local amount = GetHeroCreatures(hero, creature1)
		RemoveHeroCreatures(hero, creature1, amount)
		AddHeroCreatures(hero, creature2, amount)
	end
end

function SovereignAdd (hero, player)
	--SetPlayerResource(player, SULFUR,	GetPlayerResource(player, SULFUR) + 1);
	AddHeroCreatures(hero, 23, 1)
	AddHeroCreatures(hero, 25, 1)
	AddHeroCreatures(hero, 27, 1)
end

function AddCreatures (hero, race)
-- Haven
if race == 1 then 
	AddHeroCreatures(hero, 3, 128)
	sleep(1);
	RemoveHeroCreatures(hero, CREATURE_AIR_ELEMENTAL, 10);
	AddHeroCreatures(hero, 1, 280)
	AddHeroCreatures(hero, 5, 82)
	sleep(1)
	if IsHero(hero, "Ellaine") then  -- tier 1
		AddHeroCreatures(hero, 1, 30)
	end
	-- if IsHero(hero, "Alaric") then  -- tier 2
	-- 	AddHeroCreatures(hero, 3, 152)
	-- end
	-- if IsHero(hero, "Laszlo") then  -- tier 3
	-- 	AddHeroCreatures(hero, 5, 101)
	-- end
	AddHeroCreatures(hero, 7, 45)
	AddHeroCreatures(hero, 9, 26)
	AddHeroCreatures(hero, 11, 14)
	AddHeroCreatures(hero, 13, 6)
end

-- Inferno

if race == 2 then 
	AddHeroCreatures(hero, 17, 130) 	
	sleep(1);
	RemoveHeroCreatures(hero, CREATURE_AIR_ELEMENTAL, 10);
	AddHeroCreatures(hero, 15, 127)
	AddHeroCreatures(hero, 19, 69) 	
	sleep(1)
	-- if IsHero(hero, "Grawl")  then 
	-- 	AddHeroCreatures(hero, 19, 10)
	-- end

	AddHeroCreatures(hero, 21, 45)
	AddHeroCreatures(hero, 23, 27)
	AddHeroCreatures(hero, 25, 13)
	AddHeroCreatures(hero, 27, 7)

	if hero == "Sovereign"  then 
		SovereignAdd(hero, 3)
	end
	if hero == "Sovereign2" then
		SovereignAdd(hero, 5)
	end
end

-- Necropolis

if race == 3 then 
	AddHeroCreatures(hero, 31, 148)
	sleep(1);
	RemoveHeroCreatures(hero, CREATURE_AIR_ELEMENTAL, 10);
	AddHeroCreatures(hero, 29, 252)
	AddHeroCreatures(hero, 33, 84) 

	AddHeroCreatures(hero, 35, 45) 
	AddHeroCreatures(hero, 37, 24)
	AddHeroCreatures(hero, 39, 16)
	AddHeroCreatures(hero, 41, 9)

	if IsHero(hero, "Markal") then
		AddHeroCreatures(hero, 29, 50)
	end
end

-- Sylvan

if race == 4 then 
	AddHeroCreatures(hero, 45, 91)
	sleep(1);
	RemoveHeroCreatures(hero, CREATURE_AIR_ELEMENTAL, 10);
	AddHeroCreatures(hero, 43, 157)
	AddHeroCreatures(hero, 47, 65) 

	AddHeroCreatures(hero, 49, 38)
	AddHeroCreatures(hero, 51, 24)
	AddHeroCreatures(hero, 53, 16)		
	AddHeroCreatures(hero, 55, 6)

	if IsHero(hero, "Tieru") then 
		AddHeroCreatures(hero, 49, 4)
	end
end
-- Academy

if race == 5 then 
	AddHeroCreatures(hero, 59, 126) 
	sleep(1);
	RemoveHeroCreatures(hero, CREATURE_AIR_ELEMENTAL, 10);
	AddHeroCreatures(hero, 57, 204)
	AddHeroCreatures(hero, 61, 89) 
	sleep(1)
	if IsHero(hero, "Havez") then 
		AddHeroCreatures(hero, 57, 30)
	end

	AddHeroCreatures(hero, 63, 50)
	AddHeroCreatures(hero, 65, 32)
	AddHeroCreatures(hero, 67, 15)
	AddHeroCreatures(hero, 69, 6)
end

-- Dungeon
	
if race == 6 then 
	AddHeroCreatures(hero, 73, 57) 
	sleep(1);
	RemoveHeroCreatures(hero, CREATURE_AIR_ELEMENTAL, 10);
	AddHeroCreatures(hero, 71, 71)
	AddHeroCreatures(hero, 75, 55) 


	sleep(1)
	if IsHero(hero, "Vayshan") then 
		AddHeroCreatures(hero, 71, 10)
	end
	if IsHero(hero, "Ylaya") then 
		AddHeroCreatures(hero, 73, 5)
	end
	if IsHero(hero, "Kythra") then 
		AddHeroCreatures(hero, 75, 5)
	end

	AddHeroCreatures(hero, 77, 36)
	AddHeroCreatures(hero, 79, 22)
	AddHeroCreatures(hero, 81, 19)
	AddHeroCreatures(hero, 83, 6)
end	

-- 	Fortress

if race == 7 then 
	AddHeroCreatures(hero, 94, 136) 
	sleep(1);
	RemoveHeroCreatures(hero, CREATURE_AIR_ELEMENTAL, 10);
	AddHeroCreatures(hero, 92, 189)
	AddHeroCreatures(hero, 96, 63) 

	if IsHero(hero, "Karli") then 
		AddHeroCreatures(hero, 94, 15)
	end
	if IsHero(hero, "Ebba") then 
		AddHeroCreatures(hero, 96, 5)
	end

	AddHeroCreatures(hero, 98, 66)
	AddHeroCreatures(hero, 100, 27)
	AddHeroCreatures(hero, 102, 12)
	AddHeroCreatures(hero, 104, 5)
end	

-- Stronghold

if race == 8 then 
	AddHeroCreatures(hero, 119, 127) 
	sleep(1);
	RemoveHeroCreatures(hero, CREATURE_AIR_ELEMENTAL, 10);
	AddHeroCreatures(hero, 117, 266)
	AddHeroCreatures(hero, 121, 82) 

	sleep(1)
	-- if IsHero(hero, "Hero7") then 
	-- 	AddHeroCreatures(hero, 119, 1)
	-- end
	if IsHero(hero, "Telsek") then 
		AddHeroCreatures(hero, 121, 5)
	end


	AddHeroCreatures(hero, 123, 40) 
	AddHeroCreatures(hero, 125, 39)
	AddHeroCreatures(hero, 127, 16)	
	AddHeroCreatures(hero, 129, 5)

    if IsHero(hero, "ShakKarukat") then
        AddHeroCreatures(hero, 127, 2)	
    end

--		if hero == "Kujin" or hero == "Kujin2"  then 
--			AddHeroCreatures(hero, 123, 10) 
--		end
end
end

startThread(AddCreatures, Hero1[1], HeroRace[1])
startThread(AddCreatures, Hero1[2], HeroRace[2])

--print("CREATURES - COMPLETE");

-- =====================================================================================================================================================
-- RANDOM SKILL
-- =====================================================================================================================================================
-- 1 = Logistics
-- 2 = War Machines
-- 3 = Learning (Enlightment)
-- 4 = Leadership
-- 5 = Luck
-- 6 = Offense
-- 7 = Defense
-- 8 = Sorcery
-- 9 = Destructive Magic
-- 10 = Dark Magic 
-- 11 = Light Magic
-- 12 = Summoning Magic

-- 13 = Trainign
-- 14 = Gating
-- 15 = Necromancy
-- 16 = Avenger
-- 17 = Artificier
-- 18 = Invocaion
-- 151 = Runelore
-- 172 = Demonic Rage

-- 183 = Barbarian Enlightment
-- 187 = Voice
-- 191 = Shatter Destructive Magic
-- 195 = Shatter Dark Magic
-- 199 = Shatter Light Magic
-- 203 = Shatter Summoning Magic
-- =====================================================================================================================================================

function Skills(hero, race)
--	sleep(10);
	local random_skill_hero=0;
	local random_skill=0;

	for i=1, 2, 1 do 	
		random_skill = RandSkill[race][random(100)+1];
		if GetHeroSkillMastery(hero, random_skill) == 3 then
			while random_skill_hero == 0 do
				random_skill = RandSkill[race][random(100)+1];
				if GetHeroSkillMastery(hero, random_skill) < 3 then
					random_skill_hero = 1;
				end
			end 
		end
		GiveHeroSkill(hero, random_skill);
	end
end

Skills(Hero1[1], HeroRace[1]);
Skills(Hero1[2], HeroRace[2]);

function NecroBaseLeadership(hero, id)
	local m = GetHeroSkillMastery(hero, SKILL_LEADERSHIP);
	ChangeHeroStat(hero, 1, m);
end


if HeroRace[1] == 3 then NecroBaseLeadership(Hero1[1], 1) end
if HeroRace[2] == 3 then NecroBaseLeadership(Hero1[2], 2) end

--print("RANDOM SKILL - COMPLETE");

-- =====================================================================================================================================================
-- GOLD
-- ===================================================================================================================================================== 

function GoldNoTaken (id)
	MessageBoxForPlayers(GetPlayerFilter(id), PATH .. "no_gold_t.txt")
end

GoldLogaR = {'', ''}

function GoldLogaInit(player)
	OverrideObjectTooltipNameAndDescription('gold_left_'..player, "Text/Game/Treasures/Gold/Name.txt", PATH .. "Gold_left.txt")
	OverrideObjectTooltipNameAndDescription('gold_middle_'..player, "Text/Game/Treasures/Gold/Name.txt", PATH .. "Gold_middle.txt")
	OverrideObjectTooltipNameAndDescription('gold_right_'..player, "Text/Game/Treasures/Gold/Name.txt", PATH .. "gold_right.txt")

	Trigger(OBJECT_TOUCH_TRIGGER, 'gold_left_'..player, 'ResourcefulnessBonusPaths'..player)
	Trigger(OBJECT_TOUCH_TRIGGER, 'gold_middle_'..player, 'ResourcefulnessBonusPaths'..player)
	Trigger(OBJECT_TOUCH_TRIGGER, 'gold_right_'..player, 'ResourcefulnessBonusPaths'..player)


	RemoveObject("goldloga"..player.."_hum");
	if HeroRace[player] == 1 or HeroRace[player] == 2 or HeroRace[player] == 3 or HeroRace[player] == 4 or HeroRace[player] == 7 or HeroRace[player] == 8 then
		OverrideObjectTooltipNameAndDescription('goldloga'..player, "Text/Game/Treasures/Gold/Name.txt", PATH .. "Gold_loga.txt")
		RemoveObject("goldloga"..player.."_dung");
		RemoveObject("goldloga"..player.."_aca");
		GoldLogaR[player] = "goldloga"..player;
	end
	if HeroRace[player] == 5 then
		OverrideObjectTooltipNameAndDescription('goldloga'..player..'_aca', "Text/Game/Treasures/Gold/Name.txt", PATH .. "goldloga1_aca.txt")
		RemoveObject("goldloga"..player.."_dung");
		RemoveObject("goldloga"..player);
		GoldLogaR[player] = 'goldloga'..player..'_aca';
	end
	if HeroRace[player] == 6 then
		OverrideObjectTooltipNameAndDescription('goldloga'..player..'_dung', "Text/Game/Treasures/Gold/Name.txt", PATH .. "goldloga1_dung.txt")
		RemoveObject("goldloga"..player);
		RemoveObject("goldloga"..player.."_aca");
		GoldLogaR[player] = "goldloga"..player.."_dung";
	end
	if player == 1 then
		SetObjectPosition(GoldLogaR[player], 97, 39, 0)
	elseif player == 2 then
		SetObjectPosition(GoldLogaR[player], 98, 89, 0)
	end
	--SetObjectEnabled(GoldLogaR[player], nil);
	Trigger(OBJECT_TOUCH_TRIGGER, GoldLogaR[player], "Logistics_Artifact"..player);

	SetObjectEnabled("portal_from_altra"..player, nil)
	Trigger(OBJECT_TOUCH_TRIGGER, "portal_from_altra"..player, "GoldNoTaken("..player..")");
end

startThread(GoldLogaInit, 1);
startThread(GoldLogaInit, 2);

--goldloga1_hum goldloga1_dung goldloga1_aca

-- =====================================================================================================================================================
-- WAR MACHINES
-- =====================================================================================================================================================

function WarMachinesRemove(hero)
	RemoveHeroWarMachine(hero, 1);
	RemoveHeroWarMachine(hero, 3);
	RemoveHeroWarMachine(hero, 4);
end

startThread(WarMachinesRemove, Hero1[1]);
startThread(WarMachinesRemove, Hero1[2]);

--print("WAR MACHINES - COMPLETE");

-- =====================================================================================================================================================
-- ARTIFACTS BONUS
-- =====================================================================================================================================================

BonusArtsC = {{0, 0, 0}, {0, 0, 0}}

-- BonusArtsW = {0, 0}

-- function ArtBonus(player, hero, object);
--     while BonusArtsW[player] do
--         sleep();
--     end
--     BonusArtsW[player] = 1;
--     local c = GetHeroArtifactsCount(hero, 28);
--     local a = BonusArtsC[player][1];
--     if c > a then
--         BonusArtsC[player][1] = c;
--         local n = c - a;
--         SetPlayerResource(player, GOLD, GetPlayerResource(player, GOLD) + 2500*n);
--     end
--     if c < a then BonusArtsC[player][1] = c; end
--     c = GetHeroArtifactsCount(hero, 29);
--     a = BonusArtsC[player][2]
--     if c > a then
--         BonusArtsC[player][2] = c;
--         local n = c - a;
--         SetPlayerResource(player, GOLD, GetPlayerResource(player, GOLD) + 500*n);
--     end
--     if c < a then BonusArtsC[player][2] = c; end
--     c = GetHeroArtifactsCount(hero, 92);
--     a = BonusArtsC[player][3]
--     if c > a then
--         BonusArtsC[player][3] = c;
--         local n = c - a;
--         SetPlayerResource(player, WOOD, 	GetPlayerResource(player, WOOD)	+ 1);
--         SetPlayerResource(player, ORE, 		GetPlayerResource(player, ORE) + 1);
--         SetPlayerResource(player, MERCURY,	GetPlayerResource(player, MERCURY) + 1);
--         SetPlayerResource(player, CRYSTAL, 	GetPlayerResource(player, CRYSTAL) + 1);
--         SetPlayerResource(player, SULFUR,	GetPlayerResource(player, SULFUR) + 1);
--         SetPlayerResource(player, GEM, 		GetPlayerResource(player, GEM) + 1);
--         SetPlayerResource(player, GOLD, 	GetPlayerResource(player, GOLD) + 1);
--     end
--     BonusArtsW[player] = 0;
-- end



-- function ArtBonus1(hero, object)
--     startThread("ArtBonus", 1, hero, object);
-- end

-- function ArtBonus2(hero, object)
--     startThread("ArtBonus", 2, hero, object);
-- end

-- function ArtBonus0(player)
--     for p = 1, 4, 1 do
--         for n = 1, 6, 1 do
--             Trigger(OBJECT_TOUCH_TRIGGER, "art_p" .. player .. "i" .. p .. "n" .. n, "ArtBonus" .. player);
--         end
--     end
-- end

-- startThread(ArtBonus0, 1);
-- startThread(ArtBonus0, 2);


function ArtBonus(player, hero)
    while InfiniteLoop do
        local c = GetHeroArtifactsCount(hero, 28);
        local a = BonusArtsC[player][1];
        if c > a then
            BonusArtsC[player][1] = c;
            local n = c - a;
			GiveResources(player, GOLD, 2500*n);
        end
        if c < a then BonusArtsC[player][1] = c; end
        c = GetHeroArtifactsCount(hero, 29);
        a = BonusArtsC[player][2]
        if c > a then
            BonusArtsC[player][2] = c;
            local n = c - a;
			GiveResources(player, GOLD, 500*n);
        end
        if c < a then BonusArtsC[player][2] = c; end
        c = GetHeroArtifactsCount(hero, 92);
        a = BonusArtsC[player][3]
        if c > a then
            BonusArtsC[player][3] = c;
			for resource = 0, 6, 1 do
				startThread(GiveResources, player, resource, 1);
				sleep(2)
			end
        end
        sleep();
    end
end


startThread(ArtBonus, 1, Hero1[1]);
startThread(ArtBonus, 2, Hero1[2]);
	
-- =====================================================================================================================================================
-- LOGA BONUS
-- =====================================================================================================================================================

LogaArtsL = {
	{{86, 45}, {88, 45}, {90, 45}},
	{{82, 116}, {84, 116}, {86, 116}}
}


function LogaInit()
	local arts = Minor;
	for player = 1, 2, 1 do
		for i = 1, 3, 1 do
			local l = RandElementRemove(arts)
			local loc = LogaArtsL[player][i];
			CreateArtifact("logaArt" .. player .. "i" .. i, l, loc[1], loc[2], UNDERGROUND);
		end
	end
end

startThread(LogaInit);

function Loga(hero)
	while InfiniteLoop do
		sleep(2);	
		if GetHeroSkillMastery(hero, 1) == 1 then return 1;
		end
		if GetHeroSkillMastery(hero, 1) == 2 then return 2;
		end
		if GetHeroSkillMastery(hero, 1) == 3 then return 3;
		end
		return 0;
	end
end

function Logistics_Artifact1(hero, object)
	Logistics_Artifact(hero, object, 1);
end

function Logistics_Artifact2(hero, object)
	Logistics_Artifact(hero, object, 2);
end
	
function Logistics_Artifact(hero, object, player)
	--Trigger(OBJECT_TOUCH_TRIGGER, object, nil);
	--SetObjectEnabled(object, true);
	--MakeHeroInteractWithObject(hero, object);
	PortalFromAltraEnable(hero, object, player)
end

function LogisticsArtefactAdd(hero, player, min, max)
	for i = min, max, 1 do
		--GiveArtefact(hero, LogaArtsI[player][i]);
		MakeHeroInteractWithObject(hero, "logaArt" .. player .. "i" .. i);
	end
end


function PortalFromAltraEnable (hero, object, player)
	if HeroRace[player] == 3 or HeroRace[player] == 4 or HeroRace[player] == 5 then
		Trigger(OBJECT_TOUCH_TRIGGER, "portal_from_altra"..player, "TeleportFactionZone('"..hero.."', "..player..")");
	else
		SetObjectEnabled("portal_from_altra"..player, true);
		Trigger(OBJECT_TOUCH_TRIGGER, "portal_from_altra"..player, nil);
	end
end


--print("LOGA BONUS - COMPLETE");

-- function GenerateLogaArtifacts(player)
-- 	for i = 1, 3, 1 do
-- 		CreateArtifact("LogisticsArt_p"..player.."i"..i, LogaArtsI[player][i], LogaArtsL[player][i][1], LogaArtsL[player][i][2], UNDERGROUND);
-- 	end
-- end

TeleportFactionZoneP = {0, 0}

function TeleportFactionZone(hero, player)
	local teleporLocations = {
		[1] = {
			[3] = {81, 41, 0, 270},
			[4] = {86, 6, 0, 180},
			[5] = {49, 6, 0, 0}
		},
		 [2] = {
		 	[3] = {73, 89, 0, 270},
		 	[4] = {97, 113, 0, 180},
		 	[5] = {53, 95, 0, 180}
		}
	}
	if TeleportFactionZoneP[player] == 0 then
		TeleportFactionZoneP[player] = 1;
		local race = HeroRace[player];
		if race == 3 then
			SetObjectRotation(hero, teleporLocations[player][race][4])
			SetObjectPosition(hero, teleporLocations[player][race][1], teleporLocations[player][race][2], teleporLocations[player][race][3])
			NecroStart (hero, player)
		elseif race == 4 then
			SetObjectRotation(hero, teleporLocations[player][race][4])
			--SetObjectPosition(hero, teleporLocations[player][race][1], teleporLocations[player][race][2], teleporLocations[player][race][3])
			Avenger(hero, player)
		elseif race == 5 then
			SetObjectRotation(hero, teleporLocations[player][race][4])
			SetObjectPosition(hero, teleporLocations[player][race][1], teleporLocations[player][race][2], teleporLocations[player][race][3])
			SetArtifacterResources(hero, player);
			ArtifacterSpecBonus(hero, player);
			SetObjectOwner("academyTown"..player, player);
		end
	end
end


-- =====================================================================================================================================================
-- RESOURCEFULNESS
-- =====================================================================================================================================================

ResourcefulnessPlayer = {{0, 0}, {0, 0}}

function ResourcefulnessBonusPaths1(hero, object) ResourcefulnessBonusPaths(hero, object, 1); end
function ResourcefulnessBonusPaths2(hero, object) ResourcefulnessBonusPaths(hero, object, 2); end

function ResourcefulnessBonusPaths(hero, object, player)
	if HasHeroSkill(hero, PERK_FORTUNATE_ADVENTURER) then
		ResourcefulnessPlayer[player][2] = ResourcefulnessPlayer[player][2] + 1;
		if ResourcefulnessPlayer[player][2] == 1 then
			ResourcefulnessBonus(player, 2);
		end
	end
end

function ResourcefulnessBonus(player, n)
	local hero = Hero1[player];
	local g = 8000;
	if n == 2 then g = 2000 end
	GiveResources(player, GOLD, g)
end


-- =====================================================================================================================================================
-- SHRINES
-- =====================================================================================================================================================

OverrideObjectTooltipNameAndDescription("shrine1", PATH .. "shrine_name.txt", PATH .. "shrine_desc.txt")
OverrideObjectTooltipNameAndDescription("shrine2", PATH .. "shrine_name.txt", PATH .. "shrine_desc.txt")

OverrideObjectTooltipNameAndDescription("SpellShop11", PATH .. "spell_shop_name.txt", PATH .. "spell_shop_desc.txt")
OverrideObjectTooltipNameAndDescription("SpellShop21", PATH .. "spell_shop_name.txt", PATH .. "spell_shop_desc.txt")
if HeroRace[1] == 8 then OverrideObjectTooltipNameAndDescription("SpellShop12", PATH .. "spell_shop_name.txt", PATH .. "spell_shop_desc.txt") end
if HeroRace[2] == 8 then OverrideObjectTooltipNameAndDescription("SpellShop22", PATH .. "spell_shop_name.txt", PATH .. "spell_shop_desc.txt") end

SetObjectEnabled("shrine1", nil);
SetObjectEnabled("shrine2", nil);

Trigger(OBJECT_TOUCH_TRIGGER, "shrine1", "ShrineBonus1");
Trigger(OBJECT_TOUCH_TRIGGER, "shrine2", "ShrineBonus2");



function ShrineBonus1(hero, object)
	ShrineBonus(hero, object, HeroRace[1], 1)
end

function ShrineBonus2(hero, object)
	ShrineBonus(hero, object, HeroRace[2], 2)
end

ShrineR = {
	[1] = {
		[SPELLS_DESTRUCTIVE] = random(100),
		[SPELLS_DARK] = random(100),
		[SPELLS_LIGHT] = random(100),
		[SPELLS_SUMMONING] = random(100)
	},
	[2] = {
		[SPELLS_DESTRUCTIVE] = random(100),
		[SPELLS_DARK] = random(100),
		[SPELLS_LIGHT] = random(100),
		[SPELLS_SUMMONING] = random(100)
	}
}
ShrineVisited = {0, 0}

function ShrineBonus(hero, object, HeroRace, player)
	if ShrineVisited[player] == 1 then
		return
	end
	if HeroRace == 8 then
		Trigger(OBJECT_TOUCH_TRIGGER, object, 'Visited("' .. hero .. '")');
		local object1 = "gold_right_" .. player;
		--if IsObjectExists(object1) == 1 then MakeHeroInteractWithObject(hero, object1); sleep(1) end
		local gold = GetPlayerResource(player, GOLD);
		local sp_add = 2;
		if gold >= SpShopGold then
			sp_add = 3;
		end
		GiveHeroStat(hero, 3, sp_add)
	else
		local s = {};
		for i = 0, 3, 1 do
			local x = 0;
			if HasHeroSkill(hero, PERK_WISDOM) == 1 then
				x = 1;
			elseif GetHeroSkillMastery(hero, 9 + i) > 0 then
				x = 1;
			end

			local a, s1 = GetInternalSpellsIdToLearn(i, 1, 2 + x, player);
			s[i] = s1[mod(ShrineR[player][i],a)+1];
		end
		local gold = GetPlayerResource(player, GOLD);
		if gold >= ShrineGold then
			local msg = {
				PATH .. 'Shrine/shrine.txt';
				destructive = SPELLS[0][s[0]].name,
				dark = SPELLS[1][s[1]].name,
				light = SPELLS[2][s[2]].name,
				summoning = SPELLS[3][s[3]].name,
				gold = ShrineGold,
			}
			QuestionBoxForPlayers(GetPlayerFilter(player), msg, 'ShrineYes(' .. player .. ', ' .. player .. ', "' .. object .. '", ' .. s[0] .. ', ' .. s[1] .. ', ' .. s[2] .. ', ' .. s[3] .. ' )', 'QuestionNo')
			return
		else
			local msg = {
				PATH .. 'Shrine/shrine_no_gold.txt';
				gold = ShrineGold,
			}
			MessageBoxForPlayers(GetPlayerFilter(player), msg);
		end
	end	
end

function ShrineYes (id, player, object, destructive, dark, light, summoning)
	local hero = Hero1[id];
	if ShrineVisited[id] == 1 then return end
	if GetPlayerResource(player, GOLD) >= ShrineGold then
		ShrineVisited[id] = 1;
		SetPlayerResource(player, GOLD, GetPlayerResource(player, GOLD) - ShrineGold)

		startThread(TeachSpellInfo, hero, player, SPELLS_DESTRUCTIVE, destructive);
		sleep(2)
		startThread(TeachSpellInfo, hero, player, SPELLS_DARK, dark);
		sleep(2)
		startThread(TeachSpellInfo, hero, player, SPELLS_LIGHT, light);
		sleep(2)
		startThread(TeachSpellInfo, hero, player, SPELLS_SUMMONING, summoning);

		Trigger(OBJECT_TOUCH_TRIGGER, object, 'Visited("' .. hero .. '")');
	else
		return
	end
end


SpellPathSpells = {{{}, {}}, {{}, {}}};
SpellPathSpells[1][1].n = 0;
SpellPathSpells[1][2].n = 0;
SpellPathSpells[2][1].n = 0;
SpellPathSpells[2][2].n = 0;

function SpellPathInit(player)
	local t4f = SpellPathSpells[player][1];
	local t4 = {};
	t4.n = 0;
	local t5f = SpellPathSpells[player][2];
	local t5 = {};
	t5.n = 0;
	for i = 0, 3, 1 do
		for n = 1, SpellsAmmount[i], 1 do
			if HeroSpells[player][i][n] == 0 then
				if SPELLS[i][n].level == 4 then
					Append(t4, i*20 + n);
				elseif SPELLS[i][n].level == 5 then
					Append(t5, i*20 + n);
				end
			end
		end
	end
	for i = 1, 4, 1 do
		Append(t4f, RandElementRemove(t4));
	end
	for i = 1, 4, 1 do
		Append(t5f, RandElementRemove(t5));
	end
end

for i = 1, 2, 1 do
	if HeroRace[i] ~= 8 then
		SpellPathInit(i);
	end
	Trigger(OBJECT_TOUCH_TRIGGER, "portal_add_r"..i, "SpellPath"..i);
end

function SpellPath1(hero, object)
	SpellPath(1, hero, object);
end

function SpellPath2(hero, object)
	SpellPath(2, hero, object);
end

function SpellPath(player, hero, object)
	local race = HeroRace[player];
	SafeRemoveObject("SpellShop"..player)
	local x, y;
	MakeHeroInteractWithObject(hero, "gold_right_"..player);
	if player == 1 then
		x = 54;
		y = 39;
	else
		x = 50;
		y = 111;
	end
	if race == 8 then
		local obj;


		local ammount = 0;
		local spells = {};
		ammount, spells = GetInternalSpellsIdToLearn(SPELLS_WARCRIES, 2, 3, player);
		for i = 1, ammount, 1 do
			obj =  SPELLS[SPELLS_WARCRIES][spells[i]].ico .. player;
			SetObjectPosition(obj, x + (i * 2) - 1, y + 3);
			SetObjectEnabled(obj, nil);
			Trigger(OBJECT_TOUCH_TRIGGER, obj, "SpellPathLearnSpellQ("..player..","..SPELLS_WARCRIES..","..spells[i]..")");
		end
	else
		local school;
		local spell;
		local obj;
		local fw = 0;
		for i = 1, 4, 1 do
			-- if (SPELLS[school][spell].id == SPELL_SUMMON_ELEMENTALS) and (HasHeroSkill(hero, DEMON_FEAT_FIRE_AFFINITY)) then
			-- 	fw = 1;
			-- end
			spell = mod(SpellPathSpells[player][1][i+fw], 20);
			school = (SpellPathSpells[player][1][i+fw] - spell) / 20;
			obj = SPELLS[school][spell].ico .. player;
			SetObjectPosition(obj, x + i, y);
			SetObjectEnabled(obj, nil);
			Trigger(OBJECT_TOUCH_TRIGGER, obj, "SpellPathLearnSpellQ("..player..","..school..","..spell..")");
		end
		for i = 1, 4, 1 do
			spell = mod(SpellPathSpells[player][2][i], 20);
			school = (SpellPathSpells[player][2][i] - spell) / 20;
			obj = SPELLS[school][spell].ico .. player;
			SetObjectPosition(obj, x + i, y + 3);
			SetObjectEnabled(obj, nil);
			Trigger(OBJECT_TOUCH_TRIGGER, obj, "SpellPathLearnSpellQ("..player..","..school..","..spell..")");
		end
	end
end

SpellPathLearned = {0, 0}

function SpellPathLearnSpellQ(player, school, spell)
	if SpellPathLearned[player] > 0 then
		MessageBoxForPlayers(GetPlayerFilter(player), PATH.."SpellPath/AlreadyUsed.txt")
		return
	end
	if school == SPELLS_WARCRIES then
		SpellPathLearned[player] = SpellPathLearned[player] + 1;
		local msg = {
			PATH.."SpellPath/QuestionW.txt";
			spell = SPELLS[school][spell].name
		}
		QuestionBoxForPlayers(player, msg, "SpellPathLearnSpellY("..player..","..school..","..spell..")", "SpellPathLearnSpellN("..player..")");
	
	else
		local hero = Hero1[player];
		local spellInfo = SPELLS[school][spell];
		local t4 = 1
		if HasHeroSkill(hero, PERK_WISDOM) and HasArtefact(hero, ARTIFACT_BOOK_OF_POWER, 1) and (spellInfo.level == 4) then
			t4 = 0
		end
		if ((GetHeroSkillMastery(hero, GetMagicSchoolSkillId(school)) <= (spellInfo.level - 3)) and not (HasHeroSkill(hero, PERK_WISDOM) and HasArtefact(hero, ARTIFACT_BOOK_OF_POWER, 1) and (spellInfo.level == 4))) then
			local msg = {
				PATH.."SpellPath/NoSkill.txt";
				spell = spellInfo.name,
			}
			MessageBoxForPlayers(player, msg);
			return
		end
		if GetPlayerResource(player, GOLD) < ((spellInfo.level - 1) * 2000) then
			local msg = {
				PATH.."SpellPath/NoGold.txt";
				spell = spellInfo.name,
				gold = (spellInfo.level - 1) * 2000
			}
			MessageBoxForPlayers(player, msg);
			return
		end
		if HasHeroSkill(hero, DEMON_FEAT_FIRE_AFFINITY) and spellInfo.id == SPELL_SUMMON_ELEMENTALS then
			local msg = {
				PATH.."SpellPath/FireAffinity.txt";
				spell = spellInfo.name,
			}
			MessageBoxForPlayers(player, msg);
			return
		end

		SpellPathLearned[player] = SpellPathLearned[player] + 1;
		local msg = {
			PATH.."SpellPath/Question.txt";
			spell = SPELLS[school][spell].name,
			gold = (SPELLS[school][spell].level - 1) * 2000
		}
		QuestionBoxForPlayers(player, msg, "SpellPathLearnSpellY("..player..","..school..","..spell..")", "SpellPathLearnSpellN("..player..")");
	end
end

function SpellPathLearnSpellN(player)
	SpellPathLearned[player] = SpellPathLearned[player] - 1;
end

function SpellPathLearnSpellY(player, school, spell)
	local hero = Hero1[player];
	if SpellPathLearned[player] > 1 then
		return
	end
	TeachSpellInfo(hero, player, school, spell)
	if school == SPELLS_WARCRIES then return end
	ChangeHeroResources(player, GOLD, -((SPELLS[school][spell].level - 1) * 2000))
end


function RemoveSpellIcons()
	for s = 0, 5, 1 do
		local c = SpellsAmmount[s]
		for i = 1, c, 1 do
			for p = 1, 2, 1 do
				SafeRemoveObject(SPELLS[s][i].ico .. p)
			end
		end
	end
end


--print("SHRINES - COMPLETE");

-- =====================================================================================================================================================
-- SCOUTING
-- =====================================================================================================================================================

-- 4 = Leadership
-- 5 = Luck
-- 6 = Offense
-- 7 = Defense

ScoutingSkills1 = { 6, 7 } -- ofence, defence
ScoutingSkills2 = { 4, 5 } -- leadership, luck

ScoutingSkills1Name = { "Offence", "Defence" }
ScoutingSkills2Name = { "Leadership", "Luck" }

ScoutingRand = { {random(2)+1, random(2)+1 }, {random(2)+1, random(2)+1 } }

function Scouting(hero, player)
	local id = Opponent(player);
--	OpenCircleFog(0, 0, 0, 800, player_1)
--	OpenCircleFog(0, 0, 1, 800, player_1)

	local skill1_r = ScoutingRand[id][1];
	local skill2_r = ScoutingRand[id][2];

	local skill1 = ScoutingSkills1[skill1_r];
	local skill2 = ScoutingSkills2[skill2_r];

--	local skill1_mastery = GetHeroSkillMastery(hero, skill1);
--	local skill2_mastery = GetHeroSkillMastery(hero, skill2);

	local msg = {
		PATH .. 'Scouting.txt';
--		skill_1 = ScoutingSkills1[skill1_r],
--		skill_2 = ScoutingSkills2[skill2_r],
		skill_1_mastery = PATH .. "Skills/" .. ScoutingSkills1Name[skill1_r] .. "/" .. GetHeroSkillMastery(hero, skill1) .. ".txt",
		skill_2_mastery = PATH .. "Skills/" .. ScoutingSkills2Name[skill2_r] .. "/" .. GetHeroSkillMastery(hero, skill2) .. ".txt",
	}
	MessageBoxForPlayers(GetPlayerFilter(player), msg)

end

--'/Text/Game/Skills/Common/'
--"/Skills/"

-- =====================================================================================================================================================
-- SPHINX
-- =====================================================================================================================================================
SetObjectEnabled("sphinx1portal", nil);
SetObjectEnabled("sphinx2portal", nil);
SphinxPortal1 = {"sphinx1portal", "sphinx2portal"};
Sphinx1LvlUp = {-1, -1}
SetObjectEnabled("sphinx1", nil);
SetObjectEnabled("sphinx2", nil);
--2000 gold on begining
--42533
function Sphinx1Lvl ()
	SphinxLvl(1);
end

function Sphinx2Lvl ()
	SphinxLvl(2);
end

function SphinxLvl(player)
	Sphinx1LvlUp[player]=Sphinx1LvlUp[player]+1;

	if Sphinx1LvlUp[player] == 0 then
		QuestionBoxForPlayers(GetPlayerFilter(player),  PATH.."sphinx1.txt", 'LvlUp('..player..', 8000, 4500)', 'NoSphinx('..player..')' );
	end
	if Sphinx1LvlUp[player] == 1 then
		QuestionBoxForPlayers(GetPlayerFilter(player), PATH.."sphinx2.txt", 'LvlUp('..player..', 7000, 6000)', 'NoSphinx('..player..')' );
	end
	if Sphinx1LvlUp[player] == 2 then
		MessageBoxForPlayers(GetPlayerFilter(player), PATH.."sphinx3.txt");
	end
end

function LvlUp (player, exp1, gold1)
	if exp1==7000 then
		SetObjectEnabled(SphinxPortal1[player], true);
	end
	ChangeHeroStat(Hero1[player], 0, exp1);
	SetPlayerResource(player, 6, gold1);
end

function NoSphinx(player)
	Sphinx1LvlUp[player]=Sphinx1LvlUp[player]-1;
end


-- =====================================================================================================================================================
-- EXP STONE
-- =====================================================================================================================================================

AddExp = { -1, -1 }
ExpHero = { 0, 0 }

SetObjectEnabled('exp_obj_1', nil)
SetObjectEnabled('exp_obj_2', nil)

Trigger(OBJECT_TOUCH_TRIGGER, "exp_obj_1", "AddExp1");
Trigger(OBJECT_TOUCH_TRIGGER, "exp_obj_2", "AddExp2");

function AddExp1 (hero)
	AddExpU(hero, 1);
end

function AddExp2 (hero)
	AddExpU(hero, 2);
end

function AddExpU (hero, player)
	AddExp[player] = AddExp[player] + 1;
	ExpHero[player] = hero;
	if AddExp[player] == 0 then
		QuestionBoxForPlayers(GetPlayerFilter(player),  PATH.."exp_stone.txt", 'AddExp3("'..hero..'")', 'NoExp('..player..')' );
	end
	if AddExp[player] == 1 then
		MessageBoxForPlayers(GetPlayerFilter(player), "/Text/Game/BuildingsCommon/AlreadyVisited.txt")
	end
end

function AddExp3 (hero)
	ChangeHeroStat(hero, 0, 5000)
end

function NoExp (player_id)
	AddExp[player_id] = AddExp[player_id] - 1;
end



-- =====================================================================================================================================================
-- 4TH PATH
-- =====================================================================================================================================================

AddStat4PathVisited = { 0, 0 }

function Path4Init(player)
	SetObjectEnabled('4sciezka'..player, nil)
	Trigger(OBJECT_TOUCH_TRIGGER, '4sciezka'..player, 'AddStat4Path'..player);
	--OverrideObjectTooltipNameAndDescription('4sciezka'..player, PATH .. '4pathName.txt', PATH .. '4pathDesc.txt');
end

startThread(Path4Init, 1);
startThread(Path4Init, 2);


function AddStat4Path1(hero, object)
	AddStat4Path(hero, object, 1);
end

function AddStat4Path2(hero, object)
	AddStat4Path(hero, object, 2);
end

function AddStat4Path (hero, object, player)
	if AddStat4PathVisited[player] == 0 then
		AddStat4PathVisited[player] = AddStat4PathVisited[player] + 1;
		AddStat4Path3(hero, player);
	else
		MessageBoxForPlayers(GetPlayerFilter(player), "/Text/Game/BuildingsCommon/AlreadyVisited.txt");
	end
end


function AddStat4Path3 (hero, player)
	startThread(GiveHeroStat, hero, STAT_ATTACK, 1);
	sleep(3);
	startThread(GiveHeroStat, hero, STAT_DEFENCE, 1);
	sleep(3);
	startThread(GiveHeroStat, hero, STAT_SPELL_POWER, 1);
	sleep(3);
	startThread(GiveHeroStat, hero, STAT_KNOWLEDGE, 1);
end


-- =====================================================================================================================================================
-- END TURN MESSAGES
-- =====================================================================================================================================================

BUY_ARMY = { 0, 0 }

DarkRev = {0, 0}

FinalSequence = {0, 0}

ScoutingC = { 0, 0 }

LogisticsLevel = {0, 0}

function Messages_END(x, y, z)
	if GetDate(DAY)==y then
		MessageEND[x]=1
		if z == 1 then 
			BUY_ARMY[x] = 1;
			ScoutingC[x] = 1; 
		end
	else
		if z == 1 then
			BuyArmy(x);	
		end
	end
end

function BuyArmy(player)
	startThread(SetTownCreatures, player);
	MessageBoxForPlayers(GetPlayerFilter(player), PATH .. "BUY_ARMY.txt")
	ScoutingC[player] = 1; 
	if HasHeroSkill(Hero1[player], 222) then Messages_END_SC(Hero1[player], player); end
	Messages_END_BONUSES(player);
end

function Messages_END_SC (hero, player)
	ScoutingC[player] = 2;
	if player == 1 then Scouting(Hero1[2], player); end
	if player == 2 then Scouting(Hero1[1], player); end
end

GoldSkillCheckE = {0, 0};

function Messages_END_BONUSES (player)
	GoldSkillCheckInit(player);
end


function Messages_END_MANA(player, y)
	if GetDate(DAY)==y then
	MessageEND[player]=2
	end
	if DarkRev[player] == 0 then
		local hero = Hero1[player];
		DarkRev[player] = 1;
		if GetHeroSkillMastery(hero, 2) > 1 then GiveHeroWarMachine(hero, 4) end
		if HasHeroSkill(hero, 22) == true then GiveHeroWarMachine(hero, 3) end
		if HasHeroSkill(hero, 23) == true then GiveHeroWarMachine(hero, 1) end
		
		
		HeroLevelBonus(player, hero)
	end

	if FinalSequence[player]==0 then FinalSequence[player]=1; end
	
	sleep(3)
	
	HeroExp1[player]=1;
	
end

function HeroLevelBonus (player, hero)
	sleep(4)
	local level = GetHeroLevel(hero);
	if HasHeroSkill(hero, 140) == true or HasHeroSkill(hero, 219) == true then
		MessageBoxForPlayers(GetPlayerFilter(player), PATH.."dark_rev.txt", "DarkRevalation("..player..",'"..hero.."')");
	else
		LearningSet(player, hero);
	end
end

function DarkRevalation(player, hero)
	LevelUpHero(hero);
	sleep(8)
	LearningSet(player, hero);
end

function LearningSet(player, hero)
	local ls = LearningSetL(hero);
	if ls == 1 then
		startThread(LearningSet1, player, hero)
	elseif ls == 2 then
		startThread(LearningSet2, player, hero)
	end
end

function LearningSetL(hero)
	local l = 0;
	if HasArtefact(hero, ARTIFACT_HELM_OF_ENLIGHTMENT) then l = l + 1; end
	if HasArtefact(hero, ARTIFACT_CHAIN_MAIL_OF_ENLIGHTMENT) then l = l + 1; end
	return l
end

function LearningSet1 (player, hero)
	local stat = GetLvlStat(HeroRace[player]);
	MessageBoxForPlayers(GetPlayerFilter(player), {PATH.."learning_set1.txt";stat = GetStatName(stat)});
	sleep(10)
	GiveHeroStat(hero, stat, 1);
end

function LearningSet2 (player, hero)
	MessageBoxForPlayers(GetPlayerFilter(player), PATH.."learning_set2.txt", "LevelUpHero('"..hero.."')");
end

-- =====================================================================================================================================================
-- PORTALS
-- =====================================================================================================================================================

--function portal_sylv(player)
--	if HeroRace[(player-1)/2] ~= 4 then MessageBoxForPlayers(GetPlayerFilter(player), PATH.."nosylvan.txt"); end
--end

function SphinxPortal(player)
	if Sphinx1LvlUp[player] < 1 then
		MessageBoxForPlayers(GetPlayerFilter(player), PATH.."no_training.txt");
	end
end


-- =====================================================================================================================================================
-- AVENGER
-- =====================================================================================================================================================

function HasLvl4Avenger(hero)
    if GetHeroSkillMastery(hero, SKILL_AVENGER) == 4 or ((GetHeroSkillMastery(hero, SKILL_AVENGER) == 3) and (HasArtefact(hero, 15) == 1) and (HasArtefact(hero, 15, 1) == 0)) then
        return true
    end
    return false
end



function Avenger(hero, player)
	local r = Opponent(player);
	AvengerFight(hero, HeroRace[r], player)
end

SylvanUnitsCount = { 0, 0 };

function AvengerFight(hero, race, player) 

	UnreserveHero(hero);

	SetObjectOwner(hero, 8)
	repeat
		sleep()
	until GetObjectOwner(hero) == 8


	local unit = 21;

	local i=1;
	while unit > 0 do
		local creaturesA = GetHeroCreatures(hero, SylvanUnits[unit]);
		if creaturesA > 0 then		
			AvengerUnits[player][i] = SylvanUnits[unit];
			AvengerUnitsCount[player][i] = creaturesA;
			i=i+1;	
		end
		unit=unit-1;
	end
	AddHeroCreatures(hero, AvengerUnits[player][1], 1000);

	

	SylvanUnitsCount[player] = i-1;
	
	local creatures = {};
	local creatures_count = {};
	

	if race == 1 then
		creatures = { 1, 3, 5, 7, 9, 11, 13 };
		creatures_count = { 44, 24, 20, 10, 6, 4, 2 };
	end
	if race == 2 then
		creatures = { 15, 17, 19, 21, 23, 25, 27 };
		creatures_count = { 32, 30, 16, 10, 6, 4, 2 };
	end
	if race == 3 then
		creatures = { 29, 31, 33, 35, 37, 39, 41 };
		creatures_count = { 40, 30, 18, 10, 6, 4, 2 };
	end
	if race == 4 then
		 creatures = { 43, 45, 47, 49, 51, 53, 55 };
		 creatures_count = { 20, 18, 14, 8, 6, 4, 2 };
	end
	if race == 5 then
		 creatures = { 57, 59, 61, 63, 65, 67, 69 };
		 creatures_count = { 40, 28, 18, 10, 6, 4, 2 };
	end
	if race == 6 then
		 creatures = { 71, 73, 75, 77, 79, 81, 83 };
		 creatures_count = { 14, 10, 12, 8, 6, 4, 2 };
	end
	if race == 7 then
		 creatures = { 92, 94, 96, 98, 100, 102, 104 };
		 creatures_count = { 36, 28, 14, 12, 6, 4, 2 };
	end
	if race == 8 then
		 creatures = { 117, 119, 121, 123, 125, 127, 129 };
		 creatures_count = { 50, 28, 22, 10, 10, 4, 2 };
	end

-- SetObjectPosition(): 0 - teleportuje bez efektu, 1 - z lekkim opĂłĹşnieniem,  2-3 - natychmiastowa podrĂłĹĽ/teleport, 4 - miejscki portal, 4 < z opĂłĹşnieniem
-- 0 - HERO_BATTLE_BONUS_LUCK, 1 - HERO_BATTLE_BONUS_MORALE, 2 - HERO_BATTLE_BONUS_ATTACK, 3 - HERO_BATTLE_BONUS_DEFENCE, 4 - HERO_BATTLE_BONUS_HITPOINTS, 5 - HERO_BATTLE_BONUS_INITIATIVE, 6 - HERO_BATTLE_BONUS_SPEED, 

	--local x, y, z = GetObjectPosition(hero);

	--if id == 1 then SetObjectPosition(hero, 13, 57, 0, 0); end
	--if id == 2 then SetObjectPosition(hero, 13, 18, 0, 0); end

	--SetObjectOwner(hero, 8);


	SetObjectPosition(hero, 1, 127, -1);

	GiveHeroBattleBonus(hero, HERO_BATTLE_BONUS_HITPOINTS, 1000);
	GiveHeroBattleBonus(hero, HERO_BATTLE_BONUS_INITIATIVE, 10000);
	GiveHeroBattleBonus(hero, HERO_BATTLE_BONUS_SPEED, 10);
	GiveHeroBattleBonus(hero, HERO_BATTLE_BONUS_ATTACK, 1000);

	--SetObjectPosition(hero, x, y, z, 0);

    local creatures_t5 = creatures[1];
	local creatures_count_t5 = creatures_count[1];
	local creatures_t6 = creatures[1];
	local creatures_count_t6 = creatures_count[1];
    local creatures_t7 = creatures[1];
	local creatures_count_t7 = creatures_count[1];

	if HasHeroSkill(hero, PERK_SNIPE_DEAD) then
		creatures_t5 = creatures[5];
		creatures_count_t5 = creatures_count[5];
	end
    if IsHero(hero, "Wyngaal") then
        creatures_t6 = creatures[6];
		creatures_count_t6 = creatures_count[6];
    end
    if HasLvl4Avenger(hero) then
		creatures_t7 = creatures[7];
		creatures_count_t7 = creatures_count[7];
	end
	
	StartCombat(hero, nil, 7,
        creatures[1], creatures_count[1],
        creatures[2], creatures_count[2],
        creatures[3], creatures_count[3],
        creatures[4], creatures_count[4],
        creatures_t5, creatures_count_t5,
        creatures_t6, creatures_count_t6,
        creatures_t7, creatures_count_t7,
        nil, 'AvengerEnd(' .. player .. ')', nil, true);
end

function AvengerEnd (player)
	RemoveHeroCreatures(Hero1[player], AvengerUnits[player][1], 1000);
	local hero = Hero1[player];
	for i = 1, SylvanUnitsCount[player], 1 do
		local u = AvengerUnits[player][i];
		if u > 0 then
			local c = GetHeroCreatures(hero, u);  
			local a = AvengerUnitsCount[player][i]
			if c < a then
				AddHeroCreatures(hero, u, a - c);
			end
		end
	end
	SetObjectOwner(hero, player);
	ShowFlyingSign(PATH .. "avenger_finish.txt", hero, player, 3.0)
	if player == 1 then
		SetObjectPosition(hero, 86, 7, 0);
	elseif player == 2 then
		SetObjectPosition(hero, 97, 114	, 0);
	end
	SetObjectOwner("sylvanTown" .. player, player);
end

-- =====================================================================================================================================================
-- MINI-ARTS 
-- =====================================================================================================================================================

function SetArtifacterResources(hero, player)
    local m = GetHeroFactionalSkillMastery(hero, player);
    for i = 0, 1, 1 do
        SetPlayerResource(player, i, ArfitacterResources[m][1]);
    end
    for i = 2, 5, 1 do
        SetPlayerResource(player, i, ArfitacterResources[m][2]);
    end
end


ArtifacterSpecBonusP = {0, 0}

ArtifacterSpecBonusKnowledge = 7;

function ArtifacterSpecBonus(hero, player)
	if ArtifacterSpecBonusP[player] == 0 then
		if IsHero(hero, "Cyrus") then
			ArtifacterSpecBonusP[player] = 1;
			ChangeHeroStat(hero, 4, ArtifacterSpecBonusKnowledge);
		end
	end
end

Trigger(OBJECT_TOUCH_TRIGGER, 'akaPortal1', 'ArtifacterSpecBonusR(1)');
Trigger(OBJECT_TOUCH_TRIGGER, 'akaPortal2', 'ArtifacterSpecBonusR(2)');

function ArtifacterSpecBonusR(player)
	local hero = Hero1[player];
	if ArtifacterSpecBonusP[player] == 1 then
		ArtifacterSpecBonusP[player] = 2;
		ChangeHeroStat(hero, 4, -ArtifacterSpecBonusKnowledge);
	end
end


-- function GetPortalResources (player)

-- 	local resources = 0;

-- 	for i=0, 1, 1 do
-- 		if GetPlayerResource(player, i) < 40 then resources = resources + 1; end
-- 	end

-- 	for i=2, 5, 1 do
-- 		if GetPlayerResource(player, i) < 30 then resources = resources + 1; end
-- 	end

-- 	if resources > 1 then
-- 		return 1;
-- 	end

-- 	return 0;
-- end

--WOOD    = 0
--ORE     = 1
--MERCURY = 2
--CRYSTAL = 3
--SULFUR  = 4
--GEM     = 5
--GOLD    = 6

-- =====================================================================================================================================================
-- NECROMANCY
-- =====================================================================================================================================================

if HeroRace[1] == 3 or HeroRace[2] == 3 then

	NecroRiseCreatures = { 0, 0 }
	NecroRiseCreaturesMax = { 0, 0 }
	NecroRiseLvl = { 0, 0 }
	NecroRiseAmulet = { 0, 0 }
	NecroLord = { 0, 0 }
	
	NecroCreatures = {
	{29, 30, 152},
	{31, 32, 153},
	{33, 34, 154},
	{35, 36, 155},
	{37, 38, 156},
	{39, 40, 157},
	{41, 42, 158}
	}

	CreaturesRise = {
	{39, 68	, 97, 126},
	{19, 34, 49, 64},
	{8, 15, 21, 25},
	{4, 7, 10, 12},
	{3, 5, 6, 7},
	{1, 3, 4, 5},
	{0, 2, 3, 4},
	}

	CreaturesToRise = {
	{ 0, 0, 0, 0, 0, 0, 0 },
	{ 0, 0, 0, 0, 0, 0, 0 }
	}
	
	NecroRaised = {
	{ 0, 0, 0, 0, 0, 0, 0 },
	{ 0, 0, 0, 0, 0, 0, 0 }
	}

	CreaturesNames = {
	{"Skeleton.txt", "Skeleton_Archer.txt", "3rd/SkeletonWarrior_Name.txt"},
	{"Walking_Dead.txt", "Zombie.txt", "3rd/DiseaseZombie_Name.txt"},
	{"Manes.txt", "Ghosts.txt", "3rd/Poltergeist_Name.txt"},
	{"Vampire.txt", "Vampire_Lord.txt", "3rd/Nosferatu_Name.txt"},
	{"Lich.txt", "Demilich.txt", "3rd/LichMaster_Name.txt"},
	{"Wight.txt", "Wraith.txt", "3rd/Banshee_Name.txt"},
	{"Bone_Dragon.txt", "Shadow_Dragon.txt", "3rd/HorrorDragon_Name.txt"}
	}
	
	CreaturesNamesBase = "/Text/Game/Creatures/Necropolis/"


end



-- 71 - Amulet of Necromancy, 15 Pendant of Mastery

function GetNecromancyLvl (hero, id)
	NecroRiseCreatures[id] = 3;
	
	NecroRiseLvl[id] =  GetHeroSkillMastery(hero, 15);
	
	if NecroRiseLvl[id] < 4 then
		if (HasArtefact(hero, 15) == true) and (HasArtefact(hero, 71, 1) == false) and (HasArtefact(hero, 15, 1) == false)  then 
			NecroRiseLvl[id] = NecroRiseLvl[id] + 1;
		end
	end
	
	if HasArtefact(hero, 71, 1) then NecroRiseAmulet[id] = 1;
	elseif HasArtefact(hero, 71) == true then
		if HasArtefact(hero, 15) == false then
			NecroRiseAmulet[id] = 1;
		end
	end
	
	if NecroRiseLvl[id] == 4 then NecroRiseCreatures[id] = NecroRiseCreatures[id] + 1; end	
	
	if HasHeroSkill(hero, PERK_RAISE_ARCHERS) == true then NecroLord[id] = 1; end -- NECROMANCER_FEAT_LORD_OF_UNDEAD
	
	NecroRiseCreaturesMax[id] = NecroRiseCreatures[id];

end


function NecroInit(player)
	if HeroRace[player] == 3 then
		for i=1, 7, 1 do
			local fun = "NecQbox"..player.."(" .. i ..")";
			Trigger(OBJECT_TOUCH_TRIGGER, "necro"..player.."_" .. i, fun);
			SetObjectEnabled("necro"..player.."_" .. i, nil);
		end
		Trigger(OBJECT_TOUCH_TRIGGER, "necro"..player.."_info", "NecInfo("..player..")");
		SetObjectEnabled("necro"..player.."_info", nil);
	end
end

NecroInit(1)
NecroInit(2)

function NecQbox1(tier)
	NecQbox(1, Hero1[1], tier);
end

function NecQbox2(tier)
	NecQbox(2, Hero1[2], tier);
end

function NecQbox (player, hero, tier)

	if NecroRaised[player][tier] == 1 then return 0; end
	if NecroRiseCreatures[player] == 0 then return 0; end

	NecroRiseCreatures[player] = NecroRiseCreatures[player] - 1;

	NecroRaised[player][tier] = 1;

	local necro_bonus_add = 1 + NecroRiseAmulet[player] * 0.1 + NecroLord[player] * 0.3 + (GetHeroSkillMastery(hero, SKILL_LEADERSHIP) * 0.04);

	local nec_ar = floor(CreaturesRise[tier][NecroRiseLvl[player]] * necro_bonus_add);

	if nec_ar >= 1 then
	
		local msg = {
				PATH .. 'Necro_qbox.txt';
				creatures = NecroRiseCreatures[player] + 1,
				creatures_max = NecroRiseCreaturesMax[player],
				creatures_name = CreaturesNamesBase .. CreaturesNames[tier][ CreaturesToRise[player][tier] ],
				creatures_count = nec_ar
			}


		QuestionBoxForPlayers(GetPlayerFilter(player), msg, 'NecroAdd(' .. player .. ', ' .. tier .. ')', 'NecroNo(' .. player .. ', ' .. tier .. ')') 
	else
		MessageBoxForPlayers(GetPlayerFilter(player), PATH .. 'Necro_no.txt') 
		NecroRaised[player][tier] = 0;
		NecroRiseCreatures[player] = NecroRiseCreatures[player] + 1;
	end	
end


function NecroAdd (id, tier) -- ======================================================================
	local hero = Hero1[id];
	local necro_bonus_add = 1 + NecroRiseAmulet[id] * 0.1 + NecroLord[id] * 0.3 + (GetHeroSkillMastery(hero, SKILL_LEADERSHIP) * 0.04);

	 AddHeroCreatures(hero,	
		NecroCreatures[tier][CreaturesToRise[id][tier]],
		floor(CreaturesRise[tier][NecroRiseLvl[id]] * necro_bonus_add)
		)
		
	Trigger(OBJECT_TOUCH_TRIGGER, "necro" .. id .."_" .. tier, "NecTaken(" .. id .. ")");
	
	if NecroRiseCreatures[id] == 0 then
		TeleportToBattlePlaceHero(hero, id);
	end
	
end

function NecTaken (id)
	MessageBoxForPlayers(GetPlayerFilter(id), PATH .. "necro_taken.txt")
end

--function nec_taken_all (id)
--	MessageBoxForPlayers(GetPlayerFilter(id), PATH .. "necro_taken_all.txt")
--end

function NecroNo (id, tier)
	NecroRaised[id][tier] = 0;
	NecroRiseCreatures[id] = NecroRiseCreatures[id] + 1;
end


function NecroStart (hero, id)
	GetNecromancyLvl(hero, id);
	for i=1, 7, 1 do 
		GetNecoCreatures(hero, id, i);
	end
	for i=1, 7, 1 do 
		OverrideObjectTooltipNameAndDescription("necro" .. id .. "_" .. i, CreaturesNamesBase .. CreaturesNames[i][CreaturesToRise[id][i]], "/Text/Game/Skills/Unique/Necromancy/" .. NecroRiseLvl[id] .. "/Name.txt");
		
		OverrideObjectTooltipNameAndDescription("necro" .. id .. "_info", PATH .. "necro_info2.txt", "/Text/Game/Skills/Unique/Necromancy/" .. NecroRiseLvl[id] .. "/Name.txt");
	end
end

function GetNecoCreatures(hero, id, tier)
	if GetHeroCreatures(hero, NecroCreatures[tier][2]) > 0 then CreaturesToRise[id][tier] = 2;
	elseif GetHeroCreatures(hero, NecroCreatures[tier][3]) > 0 then CreaturesToRise[id][tier] = 3; 
	elseif GetHeroCreatures(hero, NecroCreatures[tier][1]) > 0 then CreaturesToRise[id][tier] = 1; 
	else CreaturesToRise[id][tier] = 2; end
end

function NecInfo(id)
	local hero = Hero1[id];

	local necro_bonus_add = 1 + NecroRiseAmulet[id] * 0.1 + NecroLord[id] * 0.3 + (GetHeroSkillMastery(hero, SKILL_LEADERSHIP) * 0.04);
	local msg = {
		PATH .. 'Necro_info.txt';
		creatures = NecroRiseCreatures[id],
		creatures_max = NecroRiseCreaturesMax[id],
		creature1 = floor(CreaturesRise[1][NecroRiseLvl[id]] * necro_bonus_add),
		creature2 = floor(CreaturesRise[2][NecroRiseLvl[id]] * necro_bonus_add),
		creature3 = floor(CreaturesRise[3][NecroRiseLvl[id]] * necro_bonus_add),
		creature4 = floor(CreaturesRise[4][NecroRiseLvl[id]] * necro_bonus_add),
		creature5 = floor(CreaturesRise[5][NecroRiseLvl[id]] * necro_bonus_add),
		creature6 = floor(CreaturesRise[6][NecroRiseLvl[id]] * necro_bonus_add),
		creature7 = floor(CreaturesRise[7][NecroRiseLvl[id]] * necro_bonus_add),
		creature1_name = CreaturesNamesBase .. CreaturesNames[1][ CreaturesToRise[id][1] ],
		creature2_name = CreaturesNamesBase .. CreaturesNames[2][ CreaturesToRise[id][2] ],
		creature3_name = CreaturesNamesBase .. CreaturesNames[3][ CreaturesToRise[id][3] ],
		creature4_name = CreaturesNamesBase .. CreaturesNames[4][ CreaturesToRise[id][4] ],
		creature5_name = CreaturesNamesBase .. CreaturesNames[5][ CreaturesToRise[id][5] ],
		creature6_name = CreaturesNamesBase .. CreaturesNames[6][ CreaturesToRise[id][6] ],
		creature7_name = CreaturesNamesBase .. CreaturesNames[7][ CreaturesToRise[id][7] ]
		}

	
	
	MessageBoxForPlayers(GetPlayerFilter(id), msg);
	
end


function TeleportToBattlePlaceHero(hero, player)
	if player == 1 then 
		SetObjectRotation(hero, 180)
		SetObjectPosition(hero, 58, 32, 0)

	end
	
	if player == 2 then
		SetObjectRotation(hero, 90)
		SetObjectPosition(hero, 38, 74, 0)
	end
end


-- =====================================================================================================================================================
-- GUARDIAN ANGEL
-- =====================================================================================================================================================


--guardian_power = {
--{ 41, 140, 201, 524, 1086, 2185, 4866 },
--{ 72, 203, 299, 716, 1523, 2520, 6153 }
--}

--guardian_creatures = {
--{1, 3, 5, 7, 9,  11, 13},
--{2, 4, 6, 8, 10, 12, 14},
--{106, 107, 108, 109, 110, 111, 112}
--}

--function guardian (hero, player){
--	local Guardian_1 {}
--	local Guardian_2 {}
--	local guardian1 = 0;
--	local Guardian_cr = {}
--	local creatures = {};
--	local creature_power = 0;
--	local x1 = 0;
--	local x2 = 0;
	
	
--	for i1=1, 3, 1 do
--		for i=1, 7, 1 do
--			if GetHeroCreatures(hero, guardian_creatures[i1][i]) > 0 then
				--GetHeroCreatures(hero, guardian_creatures[1][i]) * guardian_power[1][i];
--				guardian1 = guardian1 + 1;
--				Guardian_1[guardian1] = i1;
--				Guardian_2[guardian1] = i;
--				Guardian_cr[guardian1] = GetHeroCreatures(hero, guardian_creatures[i1][i])
--			end
--		end
--	end
	
	
--	for i=1, 7, 1 do
		
		
--	end


--}

-- =====================================================================================================================================================
-- TRIGGERS
-- =====================================================================================================================================================

SecondSequenceBegin = GetDate(DAY)

function TriggersInit(player)
	Trigger(OBJECT_TOUCH_TRIGGER, "sphinx"..player, "Sphinx"..player.."Lvl()");
	Trigger(OBJECT_TOUCH_TRIGGER, "sphinx1portal", "SphinxPortal(1)");
	Trigger(OBJECT_TOUCH_TRIGGER, "sphinx2portal", "SphinxPortal(2)");
	
	Trigger(REGION_ENTER_WITHOUT_STOP_TRIGGER, "und_teleport"..player, "Messages_END("..player..", " .. 1 + SecondSequenceBegin .. ", 0)");
	--Trigger(REGION_ENTER_WITHOUT_STOP_TRIGGER, "portal_town_turn"..player, "Messages_END("..player..", " .. 2 + SecondSequenceBegin .. ", 1)");
	Trigger(REGION_ENTER_WITHOUT_STOP_TRIGGER, "garrison_portal_"..player, "Messages_END_MANA("..player..", " .. 3 + SecondSequenceBegin .. ")");
	Trigger(REGION_ENTER_WITHOUT_STOP_TRIGGER, "altra"..player, "Altra("..player..")");

	Trigger(OBJECT_TOUCH_TRIGGER, "portal_add2_b"..player, "Messages_END("..player..", " .. 2 + SecondSequenceBegin .. ", 1)");
	Trigger(OBJECT_TOUCH_TRIGGER, "portal_add2_g"..player, "Messages_END("..player..", " .. 2 + SecondSequenceBegin .. ", 1)");
	Trigger(OBJECT_TOUCH_TRIGGER, "portal_add2_r"..player, "Messages_END("..player..", " .. 2 + SecondSequenceBegin .. ", 1)");
end

startThread(TriggersInit, 1);
startThread(TriggersInit, 2);

MessageEND = {1, 1}

MovementAdd[1] = -10000;
MovementAdd[2] = -10000;

Trigger (NEW_DAY_TRIGGER, "DayStart")

--print("TRIGGERS - COMPLETE");

-- =====================================================================================================================================================
-- NEW DAY TRIGGER
-- =====================================================================================================================================================

function DarkRitualG(hero, hero2)
	if HasHeroSkill(hero, PERK_DARK_RITUAL) then DarkRitual(hero, hero2); end
	if IsHero(hero, "Yrbeth") then DarkRitual(hero, hero2); DarkRitual(hero, hero2); end
end

function FinalDayBonuses(hero, hero2, race, race2, player)
	if GetHeroCreatures(hero, CREATURE_HORROR_DRAGON) > 0 then HorronDragon(player); end
	if HasHeroSkill(hero, NECROMANCER_FEAT_HERALD_OF_DEATH) then Herald(hero2) end --NECROMANCER_FEAT_HERALD_OF_DEATH
	--if race == 3 then NecroLead(hero); end
	-- sleep(1);
	BonusHP(hero)
	BonusArmy(hero, race)
	if HasHeroSkill(hero, 152) then RefreshRune(player) end
	--if HasHeroSkill(hero, WIZARD_FEAT_ARTIFICIAL_GLORY) then GiveHeroSkill(hero, WIZARD_FEAT_MARCH_OF_THE_MACHINES) end
	if GetHeroSkillMastery(hero, HERO_SKILL_RUNELORE) == 4 then UltimateRunes(player) end
	if HasHeroSkill(hero, 173) then MightOverMagic(hero) end		
    if HasHeroSkill(hero, PERK_FIRST_AID) then PlagueTent(hero) end		
	if HasHeroSkill(hero, 142) then WarlocksLuck(hero, hero2); end
    if HasLvl4Avenger(hero) then IncreaseHeroMaxStat(hero, 1); end
    if HasHeroSkill(hero, DEMON_FEAT_WEAKENING_STRIKE) or HasArtefact(hero, ARTIFACT_TOME_OF_DARK_MAGIC, 1) then WeakningStrike(hero); end
	if HasHeroSkill(hero, HERO_SKILL_BARBARIAN_WEAKENING_STRIKE) then BarbarianWeakningStrike(hero2); end
	if HasArtefact(hero, ARTIFACT_LION_HIDE_CAPE) and HasArtefact(hero, ARTIFACT_CROWN_OF_COURAGE) then LionSet(hero); end
	BonusSpells(hero, player)
end

FinalTurn=0;
FinalDay=0;

function DayStart()
	consoleCmd("dev_console_password = 'password'");
	if mod(GetDate(DAY), 7) == 1 then
		startThread(SetNilCreaturesAll);
	end

	if FirstDay == 0 then
		
		FirstDay = 1;
	
		startThread(OpenFog1)
		
		TownBuildings(Town[1], 1)
		TownBuildings(Town[2], 2)

		SetObjectOwner(Town[1], 1)
		SetObjectOwner(Town[2], 2)

	end


	if MovementAdd[1] == 0 then ChangeHeroStat(Hero1[1], 7, -10000); end
	if MovementAdd[2] == 0 then ChangeHeroStat(Hero1[2], 7, -10000); end

	MovementAdd[1] = 10000;
	MovementAdd[2] = 10000;

	if BUY_ARMY[1] == 1 then BuyArmy(1); BUY_ARMY[1] = 0; end
	if BUY_ARMY[2] == 1 then BuyArmy(2); BUY_ARMY[2] = 0; end

	Messages_END_SC(1);
	Messages_END_SC(2);

	if FinalSequence[1]==1 and FinalSequence[2]==1 then 
		FinalTurn=1;
		FinalSequence[1]=2
		FinalSequence[2]=2
		FinalDay=GetDate(DAY);
		SetRegionBlocked("garrison1", nil, PLAYER_1);

		OpenFog2()

		RemoveSpellIcons()

		if HasHeroSkill(Hero1[1], 222) then
			Scouting(Hero1[2], PLAYER_1);
			ScoutingOpenFog(PLAYER_1);
		end
		if HasHeroSkill(Hero1[2], 222) then
			Scouting(Hero1[1], PLAYER_2);
			ScoutingOpenFog(PLAYER_2);
		end
	
	end



	if GetDate(DAY) == 1 + SecondSequenceBegin then 
		Today=2;
		MessageEND[1]=0;
		MessageEND[2]=0;
		SetRegionBlocked("start_region1", nil, PLAYER_1);
		SetRegionBlocked("start_region2", nil, PLAYER_2);

	end

	if GetDate(DAY) == 2 + SecondSequenceBegin then 
		Today=3;
		MessageEND[1]=0;
		MessageEND[2]=0;
		SetRegionBlocked("underground_teleport1", nil, PLAYER_1);
		SetRegionBlocked("underground_teleport2", nil, PLAYER_2);

	end

	if GetDate(DAY) == 3 + SecondSequenceBegin then 
		Today=4;
		MessageEND[1]=0;
		MessageEND[2]=0;
		SetRegionBlocked("town_portal1", nil, PLAYER_1);
		SetRegionBlocked("town_portal2", nil, PLAYER_2);

	end

	if GetDate(DAY) == 4 + SecondSequenceBegin then
		Today=5;
		MessageEND[1]=0;
		MessageEND[2]=0;
--		SetRegionBlocked("garrison1", nil, PLAYER_1);
--		SetRegionBlocked("garrison2", nil, PLAYER_2);

	end

	if FinalTurn>0 then 
	
	

	
--		if GetDate(DAY)==FinalDay+1 then
--			MovementAdd1=0;
--			ChangeHeroStat(Hero1[1], 7, -10000);	
--		end
		if GetDate(DAY) == FinalDay then
			if HeroRace[1] == 1 then Tier6Haven(3, Hero1[1]); end
			if HeroRace[2] == 1 then Tier6Haven(5, Hero1[2]); end
			MessageEND[1]=0;
			MessageEND[2]=0;
		end
	
--		ATTACK!
		if GetDate(DAY) == FinalDay+1 then

			InfiniteLoop = false;

			MessageEND[1]=0;
			MessageEND[2]=0;
		
			sleep(8)

			local attacker = Hero1[1];
			local defender = Hero1[2];

			DarkRitualG(Hero1[1], Hero1[2])
			DarkRitualG(Hero1[2], Hero1[1])
			FinalDayBonuses(Hero1[1], Hero1[2], HeroRace[1], HeroRace[2], 1);
			FinalDayBonuses(Hero1[2], Hero1[1], HeroRace[2], HeroRace[1], 2);

			
			sleep(1)

			BonusMana(Hero1[1], HeroRace[1])
			BonusMana(Hero1[2], HeroRace[2])
			
			local x, y, z = GetObjectPosition(Hero1[1]);

			ChangeHeroStat(Hero1[1], 7, -10000);
			ChangeHeroStat(Hero1[2], 7, -10000);
			
			SetObjectPosition(Hero1[2], x, y, z, 0);
			
			sleep(2)
	
		
			while IsHeroAlive(attacker) and IsHeroAlive(defender) do
				MakeHeroInteractWithObject(attacker, defender);
				sleep(10);
			end
		end
	end
end

function Tier6Haven (id, hero)
	local removed = 0;
	local limit = 20;
	if IsHero(hero, "Isabell") then limit = 21; end
	local tier5 = Tier5HavenGet(hero);
	
	if GetHeroCreatures(hero,  11) > limit then Tier6HavenDel(hero, GetHeroCreatures(hero,  11), limit,  11, tier5); removed = 1; end
	if GetHeroCreatures(hero,  12) > limit then Tier6HavenDel(hero, GetHeroCreatures(hero,  12), limit,  12, tier5); removed = 1; end
	if GetHeroCreatures(hero, 111) > limit then Tier6HavenDel(hero, GetHeroCreatures(hero, 111), limit, 111, tier5); removed = 1; end
	
	sleep(3);
	
	if (GetHeroCreatures(hero, 11) + GetHeroCreatures(hero, 12) + GetHeroCreatures(hero, 111)) > limit then
		removed = 1;
		local what_are_you_doing = GetHeroCreatures(hero, 11) + GetHeroCreatures(hero, 12) + GetHeroCreatures(hero, 111);
		local del_creatures = what_are_you_doing - limit;
		RemoveHeroCreatures(hero, 11, del_creatures);	
		AddHeroCreatures(hero, tier5, del_creatures)
		if GetHeroCreatures(hero, 12) + GetHeroCreatures(hero, 111) > limit then
			what_are_you_doing = GetHeroCreatures(hero, 12) + GetHeroCreatures(hero, 111);
			del_creatures = what_are_you_doing - limit;
			RemoveHeroCreatures(hero, 111, del_creatures);	
			AddHeroCreatures(hero, tier5, del_creatures)
			
		end
	end
	
	if removed == 1 then
		MessageBoxForPlayers(GetPlayerFilter(id), PATH .. 'Tier6limit.txt')
	end

end

function Tier6HavenDel (hero, creatures, limit, id, tier5)
	local del_creatures = creatures - limit;
	RemoveHeroCreatures(hero, id, del_creatures);	
	AddHeroCreatures(hero, tier5, del_creatures);
end

function Tier5HavenGet (hero)
	if GetHeroCreatures(hero, 10) > 0 then return 10; end
	if GetHeroCreatures(hero, 110) > 0 then return 110; end
	if GetHeroCreatures(hero, 9) > 0 then return 9; end
	return 10;
end




function TurnEnd(x)
	ShowFlyingSign (PATH.."END_TURN.txt", Hero1[x], x, 3.0);
end
function TurnEndMana(x)
	ShowFlyingSign (PATH.."END_TURN_MANA.txt", Hero1[x], x, 3.0);
end

-- =====================================================================================================================================================
-- ON_BATTLE_END EVENT
-- =====================================================================================================================================================

function CheckVictoryCondition()
    local playersWithHeroes = {}
	local count = 0

    for player = 0, 1 do
        local hero = Hero0[player + 1]
        if hero and IsObjectExists(hero) == 1 then
            count = count + 1
            playersWithHeroes[count] = {player = player, hero = hero}
		else
			local race_id = HeroRace[player + 1] or 0
			local race_names = {
				[FACTION_HEAVEN] = "haven",
				[FACTION_ACADENY] = "academy",
				[FACTION_NECROPOLIS] = "necropolis",
				[FACTION_INFERNO] = "inferno",
				[FACTION_DUNGEON] = "dungeon",
				[FACTION_SYLVAN] = "sylvan",
				[FACTION_FORTRESS] = "fortress",
				[FACTION_STRONGHOLD] = "stronghold"
        	}
			local race = race_names[race_id] or "unknown"
			
			consoleCmd("game_writelog 1")
			print("game_won=false")
			print("castle=" .. race)
			ShowFlyingSign("Lost Detected!", "none", player, 3.0)
			consoleCmd("game_writelog 0")
		end
    end

    if count == 1 then
		local winnerInfo = playersWithHeroes[1]
        local winner = winnerInfo.player
        local hero = winnerInfo.hero
        local race_id = HeroRace[winner + 1] or 0

        local race_names = {
            [FACTION_HEAVEN] = "haven",
            [FACTION_ACADENY] = "academy",
            [FACTION_NECROPOLIS] = "necropolis",
            [FACTION_INFERNO] = "inferno",
            [FACTION_DUNGEON] = "dungeon",
            [FACTION_SYLVAN] = "sylvan",
            [FACTION_FORTRESS] = "fortress",
            [FACTION_STRONGHOLD] = "stronghold"
        }

		local race = race_names[race_id] or "unknown"
		consoleCmd("game_writelog 1")
		print("game_won=true")
		print("castle=" .. race)
		ShowFlyingSign("Victory Detected!", hero, winner, 3.0)
		consoleCmd("game_writelog 0")

		InfiniteLoop = nil
    end
end

function StartVictoryWatcher()
	while (1) do
		sleep(10)
		CheckVictoryCondition()
	end
end

startThread(StartVictoryWatcher)
-- =====================================================================================================================================================
-- LEARNING
-- =====================================================================================================================================================


LearningStats = { 0, 0 }
LearningStatsMagical = { 0, 0 }
LearningStatsNormal = { 0, 0 }
LearningStatsAll = {
{0, 0, 0, 0},
{0, 0, 0, 0}
}

LearningStatsOrder = {
{},
{}
}

--learning_stats_test = {
--{},
--{}
--}


--LvlUpStatsPercent

function UpdateLearningStats (hero, id)


	local mastery = 0;

	if HeroRace[id] < 8 then
		mastery = GetHeroSkillMastery(hero, 3)
	end
	if HeroRace[id] == 8 then
		mastery = GetHeroSkillMastery(hero, 183)
	end
	
	if mastery == 0 and LearningStats[id] == 0 then return 0; end

	local lvl = GetHeroLevel(hero);
	local faction = HeroRace[1];
	local stats_divisior = 1;
	
	local stat;
	
	local stat_del;


	if mastery == 1 then stats_divisior = 6; end
	if mastery == 2 then stats_divisior = 3; end
	if mastery == 3 then stats_divisior = 2; end
	

	local stats = floor(lvl / stats_divisior);
	
	if mastery == 0 then stats = 0; end

	 
	 
--	 sleep(30);
	 
--	local stats_to_add = stats - LearningStats[id];
	if stats > LearningStats[id] then
		while stats > LearningStats[id] do

			if LearningStatsMagical[id] <= LearningStatsNormal[id] then
				LearningStatsMagical[id] = LearningStatsMagical[id] + 1;
				LearningStats[id] = LearningStats[id] + 1;
				local random_stat = random(LvlUpStatsPercent[faction][3] + LvlUpStatsPercent[faction][4])+1;
				if random_stat <= LvlUpStatsPercent[faction][3] then
					stat = 3;				
				else 
					stat = 4;
				end
			else
				LearningStatsNormal[id] = LearningStatsNormal[id] + 1;
				LearningStats[id] = LearningStats[id] + 1;
				local random_stat = random(100)+1;

				if random_stat <= LvlUpStatsPercent[faction][1] then
					stat = 1;
				elseif random_stat <= LvlUpStatsPercent[faction][1] + LvlUpStatsPercent[faction][2] then
					stat = 2;
				elseif random_stat <= LvlUpStatsPercent[faction][1] + LvlUpStatsPercent[faction][2] + LvlUpStatsPercent[faction][3] then
					stat = 3;
				else
					stat = 4;
				end

			end
			LearningStatsAll[id][stat] = LearningStatsAll[id][stat] + 1;
			LearningStatsOrder[id][LearningStats[id]] = stat;
			GiveHeroStat(hero, stat, 1)
		end
	end
	

	while stats < LearningStats[id] do
		stat_del = LearningStatsOrder[id][LearningStats[id]];
		LearningStatsOrder[id][LearningStats[id]] = 0;
		if mod(LearningStats[id], 2) == 1 then LearningStatsMagical[id] = LearningStatsMagical[id] - 1;
		else LearningStatsNormal[id] = LearningStatsNormal[id] - 1; end
		
		ChangeHeroStat(hero, stat_del, -1);
		
		LearningStats[id] = LearningStats[id] - 1;
		LearningStatsAll[id][stat_del] = LearningStatsAll[id][stat_del] - 1;
		
		
	end
end


-- =====================================================================================================================================================
-- LVL-UP TRIGGER
-- =====================================================================================================================================================

--HERO_LEVELUP_TRIGGER

Trigger (HERO_ADD_SKILL_TRIGGER, Hero1[1], 'SkillAdd1');
Trigger (HERO_ADD_SKILL_TRIGGER, Hero1[2], 'SkillAdd2');

Trigger (HERO_REMOVE_SKILL_TRIGGER, Hero1[1], 'SkillDel1');
Trigger (HERO_REMOVE_SKILL_TRIGGER, Hero1[2], 'SkillDel2');

function SkillAdd1 (hero, skill)
	SkillAdd(hero, skill, 1)
end

function SkillAdd2 (hero, skill)
	SkillAdd(hero, skill, 2)
end

function SkillDel1 (hero, skill)
	SkillDel(hero, skill, 1)
end

function SkillDel2 (hero, skill)
	SkillDel(hero, skill, 2)
end


function SkillAdd (hero, skill, player)
	UpdateLearningStats(hero, player);
	if (HeroRace[player] == 3) and (skill == SKILL_LEADERSHIP) then GiveHeroStat(hero, 1, 1) end

--	if skill == 87 then ChangeHeroStat(hero, 3, 1) end
	if skill == 19 then GiveHeroStat(hero, 1, 1) GiveHeroStat(hero, 2, 1) end
	if skill == 26 then GiveHeroStat(hero, 3, 1) end
	if skill == 185 then GiveHeroStat(hero, 3, 1) GiveHeroStat(hero, 4, 1) end
	if skill == 222 and ScoutingC[player] == 1 then
		ScoutingC[player] = 2
		if player == 1 then Scouting(Hero1[2], PLAYER_1) end
		if player == 2 then Scouting(Hero1[1], PLAYER_2) end
	end
	if GoldSkillCheckE[player] == 1 then GoldSkillCheck(hero, player, skill) end
	
end

function SkillsInit(player)
	local hero = Hero1[player];
	for skill = 0, SkillsAmmount, 1 do
		if HasHeroSkill(hero, skill) then
			SkillAdd(hero, skill, player)
		end
	end
end

SkillsInit(PLAYER_1)
SkillsInit(PLAYER_2)

function GoldSkillCheckInit(player)
	if GoldSkillCheckE[player] == 0 then
		GoldSkillCheckE[player] = 1;
		local hero = Hero1[player];
		local l = Loga(hero);
		if LogisticsLevel[player] < l then	
			LogisticsArtefactAdd(hero, player, LogisticsLevel[player]+1, l)
			LogisticsLevel[player] = l;
		end
		if HasHeroSkill(hero, PERK_FORTUNATE_ADVENTURER) then -- resourcefulness
			if ResourcefulnessPlayer[player][1] == 0 then
				ResourcefulnessBonus(player, 1);
				ResourcefulnessPlayer[player][1] = 1;
			end
		end
	end
end


function GoldSkillCheck(hero, player, skill)
	if skill == SKILL_LOGISTICS then
		local l = Loga(hero);
		if LogisticsLevel[player] < l then	
			LogisticsArtefactAdd(hero, player, LogisticsLevel[player]+1, l)
			LogisticsLevel[player] = l;
		end
	elseif skill == PERK_FORTUNATE_ADVENTURER then
		if ResourcefulnessPlayer[player][1] == 0 then
			ResourcefulnessBonus(player, 1);
			ResourcefulnessPlayer[player][1] = 1;
		end
	end
end

function SkillDel (hero, skill, id)
--	UpdateLearningStats(hero, id);
	if (HeroRace[id] == 3) and (skill == SKILL_LEADERSHIP) then ChangeHeroStat(hero, 1, -1) end
	if skill == 19 then ChangeHeroStat(hero, 1, -1) ChangeHeroStat(hero, 2, -1) end	
	if skill == 26 then ChangeHeroStat(hero, 3, -1) end
--	if skill == 81 then ChangeHeroStat(hero, 3, 2) end
--	if skill == 87 then ChangeHeroStat(hero, 3, -1) end
	if skill == 101 then ChangeHeroStat(hero, 4, -2) end
	if skill == 131 then ChangeHeroStat(hero, 2, -1) end
	if skill == 185 then ChangeHeroStat(hero, 3, -1) ChangeHeroStat(hero, 4, -1) end
end



-- =====================================================================================================================================================
-- RESET STATS
-- =====================================================================================================================================================




-- =====================================================================================================================================================
-- PRIOR-BATTLE AND SKILLS SCRIPTS
-- =====================================================================================================================================================

function BonusMana(hero, race)

	ChangeHeroStat(hero, 8, 1000)
	ChangeHeroStat(hero, 8, 1000)

	sleep(1)

	local mana_to_add = 0;
	local kn = GetHeroStat(hero, 4)
	
	ChangeHeroStat(hero, 4, 50)
	
	--sleep(1)
	
	if race == 8 then
		if HasArtefact(hero, 47, 1) then
			mana_to_add = mana_to_add + floor(GetHeroStat(hero, 8) * 0.75);
		end
	end
	
	
	if HasHeroSkill(hero, 81) == true then	--Arcane Excellence 81/221
		mana_to_add = mana_to_add + 30; 
	end

	if HasHeroSkill(hero, 40) == true then	--Mana Regeneration
		mana_to_add = mana_to_add + 30; 
	end
	
	
	
	
	ChangeHeroStat(hero, 8, mana_to_add)

	ChangeHeroStat(hero, 4, -50)
end

function BonusHP(hero)
	local HP_to_add=0;
	if HasHeroSkill(hero, 186) == true then HP_to_add=HP_to_add+5; end --Body Building
	
	GiveHeroBattleBonus(hero, HERO_BATTLE_BONUS_HITPOINTS, HP_to_add);

end

function BonusIni (hero)
	local ini_to_add = 0;
--	if hero == "" then
--		ini_to_add = ini_to_add + 100;
--	end
	
--	if HasHeroSkill(x) then
--		ini_to_add = ini_to_add + x;
--	end
	
	GiveHeroBattleBonus(hero, HERO_BATTLE_BONUS_INITIATIVE, ini_to_add)
end

function BonusArmy(hero, race)
    local recruitment = 0;
    if HasHeroSkill(hero, 28) then recruitment = recruitment + 1; end
    if HasArtefact(hero, 71) then recruitment = recruitment + 1; end
	for n = 1, recruitment, 1 do --recruitment
		for i = 1, 24, 1 do
			if GetHeroCreatures(hero, RecruitmentCreatures[1][i]) > 0 then AddHeroCreatures(hero, RecruitmentCreatures[1][i], ceil(GetHeroCreatures(hero, RecruitmentCreatures[1][i])*0.07) + 7 ) end
			if GetHeroCreatures(hero, RecruitmentCreatures[2][i]) > 0 then AddHeroCreatures(hero, RecruitmentCreatures[2][i], ceil(GetHeroCreatures(hero, RecruitmentCreatures[2][i])*0.05) + 5 ) end
			if GetHeroCreatures(hero, RecruitmentCreatures[3][i]) > 0 then AddHeroCreatures(hero, RecruitmentCreatures[3][i], ceil(GetHeroCreatures(hero, RecruitmentCreatures[3][i])*0.03) + 3 ) end
		end
	end
	if HasHeroSkill(hero, 30) then --diplomacy
		for i=1, 24, 1 do
			if GetHeroCreatures(hero, DiplomacyCreatures[i]) > 0 then AddHeroCreatures(hero, DiplomacyCreatures[i], 1) end
		end
		if race == 3 then
			for i=1, 24, 1 do
				if GetHeroCreatures(hero, DiplomacyCreatures[i]) > 0 then AddHeroCreatures(hero, DiplomacyCreatures[i], 1) end
			end
		end
	end
	if HasHeroSkill(hero, 115) then --battle comander
		if GetHeroCreatures(hero, 45) > 0 then AddHeroCreatures(hero, 45, 10) end
		if GetHeroCreatures(hero, 46) > 0 then AddHeroCreatures(hero, 46, 10) end
		if GetHeroCreatures(hero, 146) > 0 then AddHeroCreatures(hero, 146, 10) end
	end
	if HasHeroSkill(hero, 181) then --defand us all
		if GetHeroCreatures(hero, 117) > 0 then AddHeroCreatures(hero, 117, 15) end
		if GetHeroCreatures(hero, 118) > 0 then AddHeroCreatures(hero, 118, 15) end
		if GetHeroCreatures(hero, 173) > 0 then AddHeroCreatures(hero, 173, 15) end
	end
	
	-- creatures specialists 
	
	if IsHero(hero, "Tieru") then 
		ReplaceCreatures(hero,  49, 180);
		ReplaceCreatures(hero,  50, 180);
		ReplaceCreatures(hero, 148, 181);
	end
	
    if IsHero(hero, "Kujin") then
		ReplaceCreatures(hero, 123, 182);
		ReplaceCreatures(hero, 124, 182);
		ReplaceCreatures(hero, 176, 183);
	end
	
    if IsHero(hero, "Kilghan") then
		ReplaceCreatures(hero, 117, 184);
		ReplaceCreatures(hero, 118, 184);
		ReplaceCreatures(hero, 173, 185);
	end

    if IsHero(hero, "Markal") then
		ReplaceCreatures(hero, 29, 196);
		ReplaceCreatures(hero, 30, 196);
		ReplaceCreatures(hero, 152, 197);
	end

    if IsHero(hero, "Orlando") then
		ReplaceCreatures(hero, CREATURE_DEMON, 186);
		ReplaceCreatures(hero, CREATURE_HORNED_DEMON, 186);
		ReplaceCreatures(hero, CREATURE_HORNED_LEAPER, 187);
	end

    if IsHero(hero, "Sorgal") then
		ReplaceCreatures(hero, CREATURE_RIDER, 190);
		ReplaceCreatures(hero, CREATURE_RAVAGER, 191);
		ReplaceCreatures(hero, CREATURE_BLACK_RIDER, 192);
	end

    if IsHero(hero, "Galib") then
		ReplaceCreatures(hero, CREATURE_GENIE, 193);
		ReplaceCreatures(hero, CREATURE_MASTER_GENIE, 194);
		ReplaceCreatures(hero, CREATURE_DJINN_VIZIER, 195);
	end


    
    if HasHeroSkill(hero, KNIGHT_FEAT_GUARDIAN_ANGEL) then
        ReplaceCreatures(hero, CREATURE_ARCHANGEL, 188);
		ReplaceCreatures(hero, CREATURE_SERAPH, 189);
    end
end

function DarkRitual (Hero1, hero2)
	
	local stat = GetHeroStat(hero2, 4);
	local stat_type = 4;
	if stat > GetHeroStat(hero2, 1) then
		stat = GetHeroStat(hero2, 1);
		stat_type = 1;
	end
	if stat > GetHeroStat(hero2, 3) then
		stat = GetHeroStat(hero2, 3);
		stat_type = 3;
	end
	if stat > GetHeroStat(hero2, 2) then
		stat_type = 2;
	end
	
	ChangeHeroStat(Hero1, stat_type, 1);
	ChangeHeroStat(hero2, stat_type, -1);

end

function HorronDragon (player)
	SetPlayerResource(player, CRYSTAL, GetPlayerResource(player, CRYSTAL) + 3);
end

-- function NecroLead(hero)
-- 	local m = GetHeroSkillMastery(hero, SKILL_LEADERSHIP);
-- 	if m then
-- 		ChangeHeroStat(hero, 1, m);
-- 		ChangeHeroStat(hero, 2, m);
-- 	end
-- end

function Herald(hero2)
	GiveHeroBattleBonus(hero2, HERO_BATTLE_BONUS_MORALE, -2)
end

function WarlocksLuck (Hero1, hero2)
	--ChangeHeroStat(Hero1, 5, 1);
	--ChangeHeroStat(hero2, 5, -1);
	GiveHeroBattleBonus(Hero1, HERO_BATTLE_BONUS_LUCK, 1)
	GiveHeroBattleBonus(hero2, HERO_BATTLE_BONUS_LUCK, -1)
end

function IncreaseHeroMaxStat(hero, n)
    local max = 0;
    local stat = 0;
    for i = 1, 4, 1 do
        local s = GetHeroStat(hero, i);
        if s > max then
            max = s;
            stat = i;
        end
    end
    ChangeHeroStat(hero, stat, n);
end

function PlagueTent(hero)
    GiveHeroSkill(hero, NECROMANCER_FEAT_LAST_AID);
end

function WeakningStrike(hero)
    TeachHeroSpell(hero, SPELL_SORROW);
end

function BarbarianWeakningStrike(hero2)
	GiveHeroBattleBonus(hero2, HERO_BATTLE_BONUS_ATTACK, -2)
end

function LionSet (hero)
    local lionSkills = {SKILL_OFFENCE, SKILL_DEFENCE, SKILL_SORCERY, SKILL_LEARNING}
    --local lionSkillsStat = {STAT_ATTACK, STAT_DEFENCE, STAT_SPELL_POWER, STAT_KNOWLEDGE}
    local n = 4;
    local skills = {};
	skills.n = 0;
    local s = {};
	s.n = 0;

    for i = 1, n, 1 do
        Append(skills, GetHeroSkillMastery(hero, lionSkills[i]))
    end

    local max = 0;
    for i = 1, n, 1 do
        if skills[i] > max then
            max = skills[i];
        end
    end
    if max == 0 then
        ChangeHeroStat(hero, STAT_KNOWLEDGE, 3);
        return
    end

    for i = 1, n, 1 do
        if skills[i] == max then
            Append(s, i)
        end
    end
    ChangeHeroStat(hero, RandElement(s), 3);
end


function RefreshRune (player)

	SetPlayerResource(player, WOOD, 	GetPlayerResource(player, WOOD)	+ 1);
	SetPlayerResource(player, ORE, 		GetPlayerResource(player, ORE) + 1);
	SetPlayerResource(player, MERCURY,	GetPlayerResource(player, MERCURY) + 1);
	SetPlayerResource(player, CRYSTAL, 	GetPlayerResource(player, CRYSTAL) + 1);
	SetPlayerResource(player, SULFUR,	GetPlayerResource(player, SULFUR) + 1);
	SetPlayerResource(player, GEM, 		GetPlayerResource(player, GEM) + 1);	
	
end

function UltimateRunes (player)

	SetPlayerResource(player, MERCURY,	GetPlayerResource(player, MERCURY) + 4);
	SetPlayerResource(player, CRYSTAL, 	GetPlayerResource(player, CRYSTAL) + 4);
	SetPlayerResource(player, SULFUR,	GetPlayerResource(player, SULFUR) + 4);
	SetPlayerResource(player, GEM, 		GetPlayerResource(player, GEM) + 4);	
	
end

function MightOverMagic (hero)
	local sp = floor(GetHeroStat(hero, 4)/3);
	ChangeHeroStat(hero, 3, sp);
end

function BonusSpells(hero, id)
	if HasHeroSkill(hero, 119) then
		local ammount = 0;
		local spells = {};
		for magic = 0, 3, 1 do
			local max = 2;
			if GetHeroSkillMastery(hero, magic + 9) >= 1 or HasHeroSkill(hero, 41) == 1 then max = 3 end
			local ammount1 = 0;
			local spells1 = {};
			ammount1, spells1 = GetSpellsToLearn(magic, 1, max, id);
			spells = ArrayCon(spells, ammount, spells1, ammount1);
			ammount = ammount + ammount1;
		end
		local randomspell = spells[random(ammount)+1];
		TeachHeroSpell(hero, randomspell);
		UpdateSpells(randomspell, id, 0, 3);
	end
	if HasHeroSkill(hero, 146) then
		local ammount = 0;
		local spells = {};
		local max = 2;
		if GetHeroSkillMastery(hero, 0 + 9) >= 1 or HasHeroSkill(hero, 41) == 1 then max = 3 end
		ammount, spells = GetSpellsToLearn(0, 1, max, id);		
		if ammount >= 1 then
			local randomspell = spells[random(ammount)+1];
			TeachHeroSpell(hero, randomspell);
			UpdateSpells(randomspell, id, 0, 3);
		end
	end
--	local i = 0;
--	local i1 = 0;
--	local i2 = 0;
--	if HasHeroSkill(hero, HERO_SKILL_SECRETS_OF_DESTRUCTION) then
--		if HasArtefact(hero, 76) == 0 then 
--			i = 0; --= rand(3)+1;
--			while SPELLS[SPELLS_DESTRUCTIVE][i]["level"] < 4 do i=i+1; end
--			while i2 == 0 do 
--				i1 = rand(i)+1
--				if KnowHeroSpell(hero, SPELLS[SPELLS_DESTRUCTIVE][i1]["id"]) then
--					TeachHeroSpell(hero, SPELLS[SPELLS_DESTRUCTIVE][i1]["id"])
--					i2 = 1;
--				end
--			end
--		end
--	end
end


-- =====================================================================================================================================================
-- DESCRIPTIONS
-- =====================================================================================================================================================

--Champions
--OverrideObjectTooltipNameAndDescription('Champions', PATH.."Champ_name.txt", PATH.."Champ_desc.txt")


-- =====================================================================================================================================================
-- TEMPORARY
-- =====================================================================================================================================================

--ChangeHeroStat(Hero1[1], 6, -1);
--ChangeHeroStat(Hero1[2], 6, -1);
--MessageBoxForPlayers(GetPlayerFilter(PLAYER_1)+GetPlayerFilter(PLAYER_2), PATH.."temporary.txt");

HeroExp = {0, 0}
HeroExp1 = {0, 0}
function Altra (x)
	if HeroExp[x]==0 then
		HeroExp[x]=GetHeroStat(Hero1[x], 0);
		startThread(AltraLuck, x);
	end
end

function AltraLuck (x)
	while HeroExp1[x] == 0 do
		if HeroExp[x]+100 < GetHeroStat(Hero1[x], 0) and HeroExp1[x] == 0 then
			HeroExp1[x]=1;
			--ChangeHeroStat(Hero1[x], 5, -2);
			GiveHeroBattleBonus(Hero1[x], HERO_BATTLE_BONUS_LUCK, -2)
		end
		sleep(1);
	end
end


-- =====================================================================================================================================================
-- HERO SPEC
-- =====================================================================================================================================================

--SetObjectDwellingCreatures
--SetObjectDwellingCreatures ('STRONGHOLD2', 118, k1)

--SetObjectPosition (HeroMax1, RegionToPoint 'grass')

--GetTurnTimeLeft(player)

function HeroSpecInit(player)
	local hero = Hero1[player];
	if IsHero(hero, "Inga") then
		TeachHeroSpell(hero, 249)
		TeachHeroSpell(hero, 250)
		TeachHeroSpell(hero, 251)
		TeachHeroSpell(hero, 252)			
	elseif IsHero(hero, "Thralsai") then UpgradeTownBuilding (Town[player], TOWN_BUILDING_SPECIAL_1)
	elseif IsHero(hero, "Quroq") then UpgradeTownBuilding (Town[player], TOWN_BUILDING_SPECIAL_4)
	elseif IsHero(hero, "Alaron") then ChangeHeroStat(hero, 2, 3) end
end

startThread(HeroSpecInit, 1)
startThread(HeroSpecInit, 2)



-- =====================================================================================================================================================
-- FINAL INFINITE LOOP WHICH REFRESHES MOVEMENT POINTS
-- =====================================================================================================================================================

MessageEND[1] = 1
MessageEND[2] = 1

function MovementLoop()
	local curr_plr;
	while InfiniteLoop do
		sleep(15);
		ChangeHeroStat(Hero1[1], 7, MovementAdd[1]);
		ChangeHeroStat(Hero1[2], 7, MovementAdd[2]);
		curr_plr = GetCurrentPlayer();
		if curr_plr == -1 or curr_plr == 1 then
			if MessageEND[1] == 1 then TurnEnd(1); end
			if MessageEND[1] == 2 then TurnEndMana(1); end
		end
		curr_plr = GetCurrentPlayer();
		if curr_plr == -1 or curr_plr == 2 then
			if MessageEND[2] == 1 then TurnEnd(2); end
			if MessageEND[2] == 2 then TurnEndMana(2); end
		end
		
		for i = 1, 5, 1 do
			sleep(15);
			ChangeHeroStat(Hero1[1], 7, MovementAdd[1]);
			ChangeHeroStat(Hero1[2], 7, MovementAdd[2]);
		end
	end
end

startThread(MovementLoop);