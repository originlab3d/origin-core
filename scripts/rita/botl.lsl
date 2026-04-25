// ============================================================================
// RITA AI - Script SecondLife Production
// Version 2.2.2 - FIX RADICAL anti-boucle
// ============================================================================

string API_URL = "https://originbotv1-production.up.railway.app/chat";

// --- STATE MANAGEMENT ---
integer g_busy = FALSE;
key g_last_user;
string g_last_user_name;
float g_last_interaction;
integer g_channel_used = 0;
string g_last_message = "";
key g_http_request = NULL_KEY;     // Track la requête HTTP active

// --- ANTI-SPAM CONFIG ---
float COOLDOWN_SAME_USER = 5.0;
float COOLDOWN_GLOBAL = 2.0;
float CONTEXT_WINDOW = 45.0;

// --- LIMITES MESSAGE ---
integer MAX_CHUNK_LENGTH = 800;
float CHUNK_PAUSE = 1.5;

// --- INTELLIGENCE SOCIALE ---
list NOISE_WORDS = ["lol", "mdr", "xd", "ok", "oui", "non", "++", ":)", ":(", "re", "afk", "là"];
list GREETINGS = ["salut", "coucou", "hey", "yo", "cc", "bonjour", "bonsoir", "wesh", "hello", "hi", "ciao"];

// --- PROBABILITÉS DE RÉPONSE ---
float PROB_PRIVATE = 1.00;
float PROB_MENTIONED = 1.00;
float PROB_BOB = 0.40;
float PROB_CONTEXT = 0.30;
float PROB_GREETING = 0.20;
float PROB_QUESTION = 0.30;
float PROB_RANDOM = 0.05;

// ============================================================================
// UTILS
// ============================================================================

string cleanMessage(string msg) {
    return llStringTrim(msg, STRING_TRIM);
}

string escapeJSON(string text) {
    string result = "";
    integer i;
    integer len = llStringLength(text);
    
    for (i = 0; i < len; i++) {
        string c = llGetSubString(text, i, i);
        
        if (c == "\\") {
            result += "\\\\";
        }
        else if (c == "\"") {
            result += "\\\"";
        }
        else {
            result += c;
        }
    }
    
    return result;
}

setStatus(string text, vector color) {
    llSetText("Rita\n" + text, color, 1.0);
}

// ============================================================================
// DÉCOUPAGE INTELLIGENT
// ============================================================================

list splitMessage(string msg, integer max_length) {
    list chunks = [];
    
    while (llStringLength(msg) > max_length) {
        integer cut_at = max_length;
        integer i;
        
        for (i = max_length - 1; i > max_length - 200 && i > 0; i--) {
            string c = llGetSubString(msg, i, i);
            
            if (c == "." || c == "!" || c == "?") {
                cut_at = i + 1;
                i = -1;
            }
            else if (cut_at == max_length && (c == "," || c == " ")) {
                cut_at = i + 1;
            }
        }
        
        chunks += [llStringTrim(llGetSubString(msg, 0, cut_at - 1), STRING_TRIM)];
        msg = llStringTrim(llGetSubString(msg, cut_at, -1), STRING_TRIM);
    }
    
    if (llStringLength(msg) > 0) {
        chunks += [msg];
    }
    
    return chunks;
}

// ============================================================================
// DETECTION
// ============================================================================

integer isNoise(string msg) {
    string trimmed = llStringTrim(msg, STRING_TRIM);
    if (llStringLength(trimmed) < 2) return TRUE;
    string lower = llToLower(trimmed);
    return llListFindList(NOISE_WORDS, [lower]) != -1;
}

integer isGreeting(string msg) {
    string lower = llToLower(msg);
    list words = llParseString2List(lower, [" ", ",", ".", "!", "?"], []);
    if (llGetListLength(words) == 0) return FALSE;
    string first = llList2String(words, 0);
    return llListFindList(GREETINGS, [first]) != -1;
}

integer isQuestion(string msg) {
    return llSubStringIndex(msg, "?") != -1;
}

integer isMentioned(string msg) {
    return llSubStringIndex(llToLower(msg), "rita") != -1;
}

integer isAddressedToSomeoneElse(string msg) {
    string lower = llToLower(msg);
    list gw = ["coucou ", "salut ", "hey ", "yo ", "bonjour ", "bonsoir ", "cc ", "hello ", "hi "];
    integer i;
    for (i = 0; i < llGetListLength(gw); i++) {
        if (llSubStringIndex(lower, llList2String(gw, i)) == 0) {
            if (!isMentioned(msg)) return TRUE;
        }
    }
    return FALSE;
}

// ============================================================================
// DECISION ENGINE
// ============================================================================

integer shouldRespond(string msg, string name, key id, integer channel) {
    if (channel == 110) return TRUE;
    
    string lower = llToLower(msg);
    integer mentioned = isMentioned(msg);
    
    if (isAddressedToSomeoneElse(msg)) return FALSE;
    if (llSubStringIndex(lower, "bob") != -1 && !mentioned) return FALSE;
    
    string lower_name = llToLower(name);
    if (lower_name == "bob") {
        if (llFrand(1.0) < PROB_BOB) return TRUE;
    }
    
    if (isNoise(msg) && !mentioned) return FALSE;
    if (mentioned) return TRUE;
    
    if (id == g_last_user && (llGetTime() - g_last_interaction) < CONTEXT_WINDOW) {
        if (llFrand(1.0) < PROB_CONTEXT) return TRUE;
    }
    
    if (isQuestion(msg)) {
        if (llFrand(1.0) < PROB_QUESTION) return TRUE;
    }
    
    if (isGreeting(msg)) {
        list words = llParseString2List(lower, [" "], []);
        if (llGetListLength(words) <= 2) {
            if (llFrand(1.0) < PROB_GREETING) return TRUE;
        }
    }
    
    if (llFrand(1.0) < PROB_RANDOM) return TRUE;
    return FALSE;
}

// ============================================================================
// ENVOI RÉPONSE
// ============================================================================

sendResponse(string response) {
    if (llGetAgentSize(g_last_user) == ZERO_VECTOR) return;
    
    if (llStringLength(response) <= MAX_CHUNK_LENGTH) {
        if (g_channel_used == 110) {
            llRegionSayTo(g_last_user, 0, "/me (chuchote): " + response);
        } else {
            llSay(0, response);
        }
        return;
    }
    
    list chunks = splitMessage(response, MAX_CHUNK_LENGTH);
    integer total = llGetListLength(chunks);
    integer i;
    
    for (i = 0; i < total; i++) {
        string chunk = llList2String(chunks, i);
        
        if (g_channel_used == 110) {
            llRegionSayTo(g_last_user, 0, "/me (chuchote): " + chunk);
        } else {
            llSay(0, chunk);
        }
        
        if (i < total - 1) {
            llSleep(CHUNK_PAUSE);
        }
    }
}

// ============================================================================
// MAIN STATE
// ============================================================================

default {
    state_entry() {
        llListen(0, "", NULL_KEY, "");
        llListen(110, "", NULL_KEY, "");
        
        setStatus("(Privé: /110 message)", <0.0, 1.0, 0.5>);
        llSetTimerEvent(300.0);
        
        llOwnerSay("✅ Rita v2.2.2 online");
    }
    
    listen(integer channel, string name, key id, string msg) {
        // === ANTI-BOUCLE RADICAL ===
        if (id == llGetKey()) return;
        if (llGetObjectName() == name) return;
        if (llSubStringIndex(msg, "(chuchote):") != -1) return;
        if (llSubStringIndex(msg, "réfléchit") != -1) return;
        if (llSubStringIndex(msg, "écrit") != -1) return;
        if (llSubStringIndex(msg, "observe") != -1) return;
        
        // === BUSY = IGNORE TOUT ===
        if (g_busy) {
            return;
        }
        
        // === ANTI-DOUBLON STRICT ===
        float now = llGetTime();
        
        // Même user, même message dans les 10 dernières secondes
        if (msg == g_last_message && id == g_last_user) {
            if ((now - g_last_interaction) < 10.0) {
                return;
            }
        }
        
        // Cooldown par user
        if (id == g_last_user && (now - g_last_interaction) < COOLDOWN_SAME_USER) {
            return;
        }
        
        // === DÉCISION ===
        if (!shouldRespond(msg, name, id, channel)) return;
        
        // === LOCK ET ENVOI ===
        g_busy = TRUE;
        g_last_user = id;
        g_last_user_name = name;
        g_last_interaction = now;
        g_channel_used = channel;
        g_last_message = msg;
        
        setStatus("réfléchit...", <1.0, 1.0, 0.0>);
        
        string safe_msg = escapeJSON(cleanMessage(msg));
        string safe_name = escapeJSON(cleanMessage(name));
        
        string is_private_str;
        if (channel == 110) {
            is_private_str = "true";
        } else {
            is_private_str = "false";
        }
        
        string payload = "{\"message\":\"" + safe_msg + 
                        "\",\"user\":\"" + safe_name + 
                        "\",\"is_private\":" + is_private_str + "}";
        
        // TRACK la requête HTTP
        g_http_request = llHTTPRequest(API_URL, [
            HTTP_METHOD, "POST",
            HTTP_MIMETYPE, "application/json",
            HTTP_BODY_MAXLENGTH, 16384
        ], payload);
        
        llSetTimerEvent(30.0);
    }
    
    http_response(key req_id, integer status, list meta, string body) {
        // === IGNORE LES RÉPONSES QUI NE SONT PAS LA NÔTRE ===
        if (req_id != g_http_request) {
            return;
        }
        
        // Reset
        g_http_request = NULL_KEY;
        llSetTimerEvent(300.0);
        
        if (status != 200) {
            llOwnerSay("⚠️ API Error " + (string)status);
            g_busy = FALSE;
            setStatus("(Privé: /110 message)", <0.0, 1.0, 0.5>);
            return;
        }
        
        string response = llJsonGetValue(body, ["response"]);
        
        if (response == JSON_INVALID || response == "" || llStringLength(response) < 2) {
            g_busy = FALSE;
            setStatus("(Privé: /110 message)", <0.0, 1.0, 0.5>);
            return;
        }
        
        // Typing
        setStatus("écrit...", <0.0, 1.0, 0.0>);
        float typing_time = llStringLength(response) * 0.035;
        if (typing_time > 3.5) typing_time = 3.5;
        if (typing_time < 0.8) typing_time = 0.8;
        llSleep(typing_time);
        
        // Envoi
        sendResponse(response);
        
        // Cooldown
        llSleep(COOLDOWN_GLOBAL);
        
        g_busy = FALSE;
        setStatus("(Privé: /110 message)", <0.0, 1.0, 0.5>);
    }
    
    timer() {
        if (g_busy) {
            llOwnerSay("⚠️ Timeout - reset");
            g_busy = FALSE;
            g_http_request = NULL_KEY;
            setStatus("(Privé: /110 message)", <0.0, 1.0, 0.5>);
            llSetTimerEvent(300.0);
            return;
        }
        
        llSensor("", NULL_KEY, AGENT, 20.0, PI);
    }
    
    sensor(integer num) {
        if (!g_busy && num > 0 && llFrand(1.0) < 0.03) {
            g_busy = TRUE;
            setStatus("observe...", <1.0, 1.0, 0.0>);

            // user != "System" pour ne pas être filtré par is_system_event côté serveur
            string payload = "{\"message\":\"[IDLE] des gens sont là\",\"user\":\"Ambiance\",\"is_private\":false}";

            g_http_request = llHTTPRequest(API_URL, [
                HTTP_METHOD, "POST",
                HTTP_MIMETYPE, "application/json",
                HTTP_BODY_MAXLENGTH, 16384
            ], payload);

            llSetTimerEvent(30.0);
        }
    }
    
    no_sensor() {
    }
    
    changed(integer change) {
        if (change & CHANGED_REGION) {
            llResetScript();
        }
    }
}