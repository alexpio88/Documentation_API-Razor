# -*- coding: utf-8 -*-
# =============================================================================
#  ICE DEXXER BANDAGE HELPER  |  Razor Enhanced (IronPython)
#  Versione: 2.8.0 (REWRITE: Mani Libere, Auto-Pull Bende & Stabilità)
# =============================================================================

import time

# ┌─────────────────────────────────────────────────────────────────────────┐
# │                       ZONA IMPOSTAZIONI                                 │
# └─────────────────────────────────────────────────────────────────────────┘

STR_BUFFED_VALUE       = 127
DEX_BUFFED_VALUE       = 134
STAM_REFRESH_THRESHOLD = 120
HEAL_TRIGGER_HP_PCT    = 98

# Bushido: Confidence ha priorità quando serve recupero, Counter Attack quando
# si sta reggendo bene il fight e non ci sono urgenze difensive.
BUSHIDO_ENABLED              = True
BUSHIDO_MIN_MANA             = 10
CONFIDENCE_HP_PCT            = 90
CONFIDENCE_STAM_THRESHOLD    = 80
CONFIDENCE_COOLDOWN_SEC      = 8
COUNTER_ATTACK_MIN_HP_PCT    = 95
COUNTER_ATTACK_COOLDOWN_SEC  = 6

# ID Oggetti
BANDAGE_ID             = 0x0E21
FIRST_AID_BELT_ID      = 0xA1F6
GREATER_CURE_ID        = 0x0F07
ENCHANTED_APPLE_ID     = 0x2FD8
GREATER_STR_ID         = 0x0F09
GREATER_AGI_ID         = 0x0F08
GREATER_REFRESH_ID     = 0x0F0B
GREATER_EXPLO_ID       = 0x0F0D

# Cooldown e Tempistiche
APPLE_COOLDOWN_SEC     = 31
TALISMAN_COOLDOWN_SEC  = 1200  # Regola in base al tuo server (es. Outlands/Demise)
FAST_BUFF_DELAY_MS     = 200
COUNTER_HUE            = 0x3E
COUNTER_TICK_MS        = 150

# Explosion System Settings
EXPLO_FUSE_TIME_MS       = 3000
EXPLO_FLIGHT_MS_PER_TILE = 60
EXPLO_MAX_RANGE          = 10
EXPLO_FALLBACK_TILES     = 3
EXPLO_HUE_ALERT          = 0x26

# ┌─────────────────────────────────────────────────────────────────────────┘

# Variabili di Stato Globali
_last_apple_time = 0.0
_last_talisman_time = 0.0
_estimated_ping = 100
_explo_armed = False
_explo_armed_time = 0
_explo_target_serial = None
_last_confidence_time = 0.0
_last_counter_attack_time = 0.0

# ═══════════════════════════════════════════════════════════════════════════
# UTILITY & GESTIONE INVENTARIO
# ═══════════════════════════════════════════════════════════════════════════

def msg(text, hue=68):
    Misc.SendMessage("[Ice Helper] " + str(text), hue)

def bandage_seconds():
    """Calcola i secondi della benda in base alla Dex corrente."""
    dex = Player.Dex
    secs = 11.0 - (float(dex) / 20.0)
    return max(2.0, secs)

def current_hp_percent():
    """Restituisce la percentuale vita corrente evitando divisioni per zero."""
    return int(float(Player.Hits) / Player.HitsMax * 100) if Player.HitsMax > 0 else 100

def restock_bandages_from_belt():
    """Se non ci sono bende nel backpack, ne sposta 20 dalla First Aid Belt."""
    backpack_bandages = Items.FindByID(BANDAGE_ID, -1, Player.Backpack.Serial)
    if not backpack_bandages:
        belt = Items.FindByID(FIRST_AID_BELT_ID, -1, Player.Backpack.Serial)
        if belt:
            belt_bandages = Items.FindByID(BANDAGE_ID, -1, belt.Serial)
            if belt_bandages:
                msg("Estrazione bende dalla First Aid Belt...", 50)
                Items.Move(belt_bandages, Player.Backpack.Serial, 20)
                Misc.Pause(300) # Delay di sicurezza per il server

def find_item_in_pack(item_id):
    """Cerca un oggetto direttamente nel backpack principale."""
    return Items.FindByID(item_id, -1, Player.Backpack.Serial)

def use_potion(item_id):
    """Beve una pozione assicurandosi di avere le mani libere se necessario."""
    pot = find_item_in_pack(item_id)
    if not pot:
        return False

    # Controllo mani occupate (Arma a 2 mani o scudo)
    left_hand = Player.GetItemOnLayer('LeftHand')
    right_hand = Player.GetItemOnLayer('RightHand')
    had_to_disarm = False

    # Se entrambe le mani sono occupate o c'è un'arma a due mani
    if left_hand and right_hand:
        had_to_disarm = True
        Items.UnEquipItem(left_hand)
        Misc.Pause(100)

    # Beve la pozione
    Items.UseItem(pot)

    # Se abbiamo disarmato qualcosa, lo riequipaggiamo immediatamente
    if had_to_disarm and left_hand:
        Misc.Pause(100)
        Player.EquipItem(left_hand)

    return True

# ═══════════════════════════════════════════════════════════════════════════
# DIFESA RAPIDA (CURA, APPLE & TALISMANO)
# ═══════════════════════════════════════════════════════════════════════════

def check_security_immediate():
    global _last_apple_time, _last_talisman_time

    # 1. Priorità Assoluta: Cura Veleno
    if Player.Poisoned:
        use_potion(GREATER_CURE_ID)

    # 2. Controllo Contro-Mortal / Maledizioni
    if Player.BuffsExist("Mortal Strike"):
        # Tentativo 1: Enchanted Apple
        if (time.time() - _last_apple_time) >= APPLE_COOLDOWN_SEC:
            apple = find_item_in_pack(ENCHANTED_APPLE_ID)
            if apple:
                Items.UseItem(apple)
                _last_apple_time = time.time()
                msg("Mortal rimosso con Apple!", 68)
                return

        # Tentativo 2: Talismano (Se l'apple è in cooldown)
        if (time.time() - _last_talisman_time) >= TALISMAN_COOLDOWN_SEC:
            talisman = Player.GetItemOnLayer('Talisman')
            if talisman:
                Items.UseItem(talisman)
                if Target.WaitForTarget(1000, False):
                    Target.TargetExecute(Player.Serial)
                    _last_talisman_time = time.time()
                    msg("Mortal rimosso con Talismano!", 68)

# ═══════════════════════════════════════════════════════════════════════════
# ADVANCED EXPLOSION POTION LOGIC
# ═══════════════════════════════════════════════════════════════════════════

def get_best_target():
    target = Target.GetLastAttack()
    if target and target != Player.Serial: return target
    last = Target.GetLast()
    if last and last != Player.Serial: return last
    return None

def is_attacking_valid_target():
    """Verifica che il player sia in combat e abbia un target mobile valido."""
    if not Player.WarMode:
        return False

    target_serial = get_best_target()
    if not target_serial:
        return False

    return Mobiles.FindBySerial(target_serial) is not None

def check_bushido_combat():
    """Gestisce Confidence e Counter Attack in base allo stato del combattimento."""
    global _last_confidence_time, _last_counter_attack_time

    if not BUSHIDO_ENABLED or _explo_armed:
        return
    if not is_attacking_valid_target():
        return
    if Player.Mana < BUSHIDO_MIN_MANA:
        return

    now = time.time()
    hp_pct = current_hp_percent()
    needs_confidence = hp_pct <= CONFIDENCE_HP_PCT or Player.Stam <= CONFIDENCE_STAM_THRESHOLD

    # Se serve recupero, Confidence ha precedenza e blocca Counter Attack.
    if needs_confidence:
        if (not Player.BuffsExist("Confidence") and
            (now - _last_confidence_time) >= CONFIDENCE_COOLDOWN_SEC):
            Spells.CastBushido("Confidence", False)
            _last_confidence_time = now
            msg("Bushido: Confidence per recupero HP/Stam.", 68)
        return

    if hp_pct < COUNTER_ATTACK_MIN_HP_PCT:
        return
    if Player.BuffsExist("Counter Attack") or Player.BuffsExist("Confidence"):
        return
    if (now - _last_counter_attack_time) < COUNTER_ATTACK_COOLDOWN_SEC:
        return

    Spells.CastBushido("Counter Attack", False)
    _last_counter_attack_time = now
    msg("Bushido: Counter Attack pronto.", 68)

def get_safety_drop_coords():
    """Calcola le coordinate a terra dietro/vicino al player in caso di emergenza."""
    px, py, pz = Player.Position.X, Player.Position.Y, Player.Position.Z
    direction = Player.Direction
    dx, dy = 0, 0
    if direction == 0: dy = -EXPLO_FALLBACK_TILES   # North
    elif direction == 2: dx = EXPLO_FALLBACK_TILES  # East
    elif direction == 4: dy = EXPLO_FALLBACK_TILES  # South
    elif direction == 6: dx = -EXPLO_FALLBACK_TILES # West
    return px + dx, py + dy, pz

def handle_explo_request():
    global _explo_armed, _explo_armed_time, _explo_target_serial, _estimated_ping
    if _explo_armed: return

    explo = find_item_in_pack(GREATER_EXPLO_ID)
    if not explo:
        msg("Nessuna pozione Explosion trovata!", 33)
        return

    # Calcolo dinamico del ping basato sulla comparsa del target
    start_click = int(time.time() * 1000)
    Items.UseItem(explo)

    if Target.WaitForTarget(1500, False):
        _estimated_ping = (int(time.time() * 1000) - start_click)
        _explo_armed_time = int(time.time() * 1000)
        _explo_target_serial = get_best_target()
        _explo_armed = True
        msg("BOMBA INNESCATA! (Ping stimato: {}ms)".format(_estimated_ping), 50)
    else:
        msg("Errore di innesco (Target non apparso)!", 33)

def check_explo_throw():
    global _explo_armed, _explo_armed_time
    if not _explo_armed: return

    elapsed = int(time.time() * 1000) - _explo_armed_time
    safety_margin = int(_estimated_ping * 1.2)
    critical_time = EXPLO_FUSE_TIME_MS - safety_margin

    mob = Mobiles.FindBySerial(_explo_target_serial) if _explo_target_serial else None

    if mob:
        dist = max(abs(Player.Position.X - mob.Position.X), abs(Player.Position.Y - mob.Position.Y))
        if dist <= EXPLO_MAX_RANGE:
            # Calcolo del tempo di volo ottimale basato sulla distanza dal bersaglio
            optimal_time = EXPLO_FUSE_TIME_MS - (dist * EXPLO_FLIGHT_MS_PER_TILE) - safety_margin
            if elapsed >= optimal_time:
                Target.TargetExecute(_explo_target_serial)
                msg("LANCIATA! (Distanza: {})".format(dist), EXPLO_HUE_ALERT)
                _explo_armed = False
        else:
            # Bersaglio fuori portata: scarica la bomba a terra prima che esploda in mano
            if elapsed >= critical_time:
                x, y, z = get_safety_drop_coords()
                Target.TargetExecute(x, y, z)
                msg("Target fuori range! Poto buttata a terra.", 33)
                _explo_armed = False
    else:
        # Nessun bersaglio valido: scarica a terra di sicurezza
        if elapsed >= critical_time:
            x, y, z = get_safety_drop_coords()
            Target.TargetExecute(x, y, z)
            msg("Nessun target! Poto buttata a terra.", 33)
            _explo_armed = False

# ═══════════════════════════════════════════════════════════════════════════
# LOOP PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════

msg("Ice Helper v2.8.0 Attivo ed Ottimizzato!", 68)

while Player.Connected:
    # 1. Controlli di sicurezza immediati ad ogni inizio ciclo
    check_security_immediate()

    # 2. Intercettazione comando lancio Explosion da Hotkey esterna
    if Misc.ReadSharedValue('throw_explo') == True:
        Misc.RemoveSharedValue('throw_explo')
        handle_explo_request()
    check_explo_throw()
    check_bushido_combat()

    # 3. SISTEMA DI GUARIGIONE (BENDE AUTOMATICHE)
    current_hp_pct = current_hp_percent()

    if current_hp_pct < HEAL_TRIGGER_HP_PCT:
        restock_bandages_from_belt()  # Verifica ed eventuale rifornimento bende
        bende = find_item_in_pack(BANDAGE_ID)

        if bende:
            durata_ms = int(bandage_seconds() * 1000)
            inizio_benda = int(time.time() * 1000)

            Items.UseItem(bende)
            if Target.WaitForTarget(1000, False):
                Target.TargetExecute(Player.Serial)

            # Sub-loop di attesa asincrona (Evita il congelamento dello script durante la benda)
            while Player.Connected:
                ora = int(time.time() * 1000)
                passato = ora - inizio_benda

                if passato >= durata_ms:
                    Player.HeadMessage(COUNTER_HUE, "[ OK ]")
                    break

                # Feedback visivo sopra la testa del PG
                rimanente = (durata_ms - passato) / 1000.0
                Player.HeadMessage(COUNTER_HUE, "[ {:.1f}s ]".format(rimanente))

                # Attività critiche eseguite *durante* l'applicazione della benda
                check_security_immediate()
                if Misc.ReadSharedValue('throw_explo') == True:
                    Misc.RemoveSharedValue('throw_explo')
                    handle_explo_request()
                check_explo_throw()
                check_bushido_combat()

                Misc.Pause(COUNTER_TICK_MS)
            Misc.Pause(200)

    # 4. GESTIONE AUTOMATICA POTION BUFF (In modalità combattimento)
    if Player.WarMode:
        if Player.Str < STR_BUFFED_VALUE:
            use_potion(GREATER_STR_ID)
            Misc.Pause(FAST_BUFF_DELAY_MS)
        if Player.Dex < DEX_BUFFED_VALUE:
            use_potion(GREATER_AGI_ID)
            Misc.Pause(FAST_BUFF_DELAY_MS)
        if Player.Stam < STAM_REFRESH_THRESHOLD:
            use_potion(GREATER_REFRESH_ID)
            Misc.Pause(FAST_BUFF_DELAY_MS)

    Misc.Pause(100)
