# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSelection, getConfigListEntry
from enigma import eServiceReference, iServiceInformation
from os import system, listdir, path, remove, makedirs
from twisted.web import resource, server, static
from twisted.internet import reactor
import urllib.parse
import json

# --- Configuración ---
PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/descargador"
SETTINGS_FILE = path.join(PLUGIN_PATH, "settings.json")
MP3_DIR = "/media/hdd/Mp3"
PORT = 7447

def get_settings():
    default = {"player": "4097"} # GStreamer por defecto suele ser más compatible
    if path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f: return json.load(f)
        except: pass
    return default

def save_settings(player_id):
    try:
        if not path.exists(PLUGIN_PATH): makedirs(PLUGIN_PATH)
        with open(SETTINGS_FILE, "w") as f: json.dump({"player": player_id}, f)
    except: pass

# --- Interfaz Enigma2 ---
class DescargadorConfig(Screen, ConfigListScreen):
    skin = """<screen position="center,center" size="550,150" title="Ajustes">
        <widget name="config" position="10,20" size="530,40" />
        <eLabel text="by Zoubair" position="10,65" size="530,25" font="Regular;16" halign="right" foregroundColor="#666666" transparent="1" />
        <eLabel text="OK: Guardar | EXIT: Salir" position="10,105" size="530,25" font="Regular;18" halign="center" foregroundColor="#facc15" />
    </screen>"""
    def __init__(self, session):
        Screen.__init__(self, session)
        settings = get_settings()
        self.player_choice = ConfigSelection(choices=[("4097","GStreamer"),("5001","GstPlayer"),("5002","ExtPlayer3")], default=settings["player"])
        self.list = [getConfigListEntry("Reproductor:", self.player_choice)]
        ConfigListScreen.__init__(self, self.list, session)
        self["setup_actions"] = ActionMap(["SetupActions"], {"ok": self.save, "cancel": self.close}, -2)

    def save(self):
        save_settings(self.player_choice.value)
        self.close()

class DescargadorPlayer(Screen):
    skin = """<screen name="DescargadorPlayer" position="center,center" size="900,600" title="Descargador Multimedia" backgroundColor="#101010">
        <widget name="status" position="20,15" size="500,40" font="Regular;26" foregroundColor="#2ecc71" transparent="1" />
        <eLabel text="by Zoubair" position="550,20" size="330,30" font="Regular;20" halign="right" foregroundColor="#444444" transparent="1" />
        <widget name="filelist" position="20,70" size="860,450" scrollbarMode="showOnDemand" itemHeight="45" transparent="1" />
        <widget name="info" position="20,545" size="860,30" font="Regular;20" halign="center" foregroundColor="#aaaaaa" transparent="1" />
    </screen>"""
    def __init__(self, session):
        Screen.__init__(self, session)
        self["filelist"] = MenuList([])
        self["status"] = Label("Lista de archivos")
        self["info"] = Label("OK: Reproducir | MENU: Ajustes | EXIT: Salir")
        self["actions"] = ActionMap(["OkCancelActions", "MenuActions"], {"ok": self.onOk, "cancel": self.close, "menu": self.openConfig}, -1)
        
        self.onShow.append(self.cargarArchivos)

    def openConfig(self): 
        self.session.openWithCallback(self.cargarArchivos, DescargadorConfig)

    def cargarArchivos(self):
        display_list = []
        if not path.exists(MP3_DIR):
            try: makedirs(MP3_DIR)
            except: pass
        
        if path.exists(MP3_DIR):
            items = sorted(listdir(MP3_DIR), reverse=True)
            display_list = [f for f in items if f.lower().endswith(('.mp3', '.m4a', '.mp4')) and path.isfile(path.join(MP3_DIR, f))]
        
        self["filelist"].setList(display_list)
        if len(display_list) == 0:
            self["status"].setText("Carpeta vacía")
        else:
            self["status"].setText("Archivos: %d" % len(display_list))

    def onOk(self):
        sel = self["filelist"].getCurrent()
        if not sel: return
        ruta = path.join(MP3_DIR, sel)
        
        if not path.exists(ruta):
            self.cargarArchivos()
            return
            
        # Limpiar marcas de reproducción anterior
        system('rm -f "%s.cuts"' % ruta)
        
        settings = get_settings()
        p_type = settings.get("player", "4097")
        
        # IMPORTANTE: Construir el ServiceReference correctamente para archivos locales
        # Formato: 4097:0:1:0:0:0:0:0:0:0:RUTA_DEL_ARCHIVO
        sref = eServiceReference(int(p_type), 0, ruta)
        sref.setName(sel)
        
        print("[Descargador] Reproduciendo: %s con tipo %s" % (ruta, p_type))
        self.session.nav.stopService()
        self.session.nav.playService(sref)

# --- Servidor Web ---
class FastWebResource(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild(b"stream", static.File(MP3_DIR))

    def getChild(self, name, request):
        if name == b"": return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        request.setHeader(b"content-type", b"text/html; charset=utf-8")
        request.setHeader(b"cache-control", b"no-cache, no-store, must-revalidate")
        request.setHeader(b"pragma", b"no-cache")
        request.setHeader(b"expires", b"0")
        
        archivos_html = ""
        if path.exists(MP3_DIR):
            archivos = sorted([f for f in listdir(MP3_DIR) if f.lower().endswith(('.mp3', '.m4a', '.mp4')) and path.isfile(path.join(MP3_DIR, f))], reverse=True)
            
            if not archivos:
                archivos_html = "<div style='padding:20px; color:#666; text-align:center;'>La carpeta está vacía.</div>"
            else:
                for f in archivos:
                    url_stream = "/stream/" + urllib.parse.quote(f)
                    archivos_html += """
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#252525; padding:10px; margin-bottom:5px; border-radius:8px;">
                        <span style="font-size:14px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1; color:#ddd; margin-right:10px;">{0}</span>
                        <div style="display:flex; gap:5px;">
                            <a href="{1}" target="_blank" style="background:#3498db; color:white; padding:8px 12px; font-size:12px; text-decoration:none; border-radius:5px; font-weight:bold;">PLAY</a>
                            <form method="POST" style="margin:0; display:inline;" onsubmit="return confirm('¿Borrar archivo?')">
                                <input type="hidden" name="action" value="delete">
                                <input type="hidden" name="filename" value="{0}">
                                <button type="submit" style="background:#e74c3c; color:white; padding:8px 12px; font-size:12px; width:auto; border-radius:5px; border:none; cursor:pointer;">BORRAR</button>
                            </form>
                        </div>
                    </div>""".format(f, url_stream)

        html = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background:#0f0f0f; color:white; font-family:sans-serif; margin:0; padding:20px; display:flex; flex-direction:column; align-items:center; }}
            .container {{ width:100%; max-width:500px; padding:20px; border-radius:20px; background:#1a1a1a; border:1px solid #333; box-shadow: 0 10px 30px rgba(0,0,0,0.5); box-sizing:border-box; position:relative; }}
            .author {{ position:absolute; top:10px; right:20px; font-size:12px; color:#555; font-weight:bold; }}
            h1 {{ color:#2ecc71; text-align:center; margin-bottom:20px; margin-top:10px; }}
            input[type="text"] {{ width:100%; padding:15px; font-size:16px; border-radius:10px; border:2px solid #333; background:#252525; color:white; margin-bottom:15px; box-sizing:border-box; outline:none; }}
            .btn-group {{ display: flex; gap: 10px; margin-bottom:25px; }}
            button {{ flex:1; padding:15px; font-size:14px; font-weight:bold; border-radius:10px; border:none; cursor:pointer; text-transform:uppercase; }}
            .btn-audio {{ background:#2ecc71; color:black; }}
            .btn-video {{ background:#3498db; color:white; }}
            .list-container {{ width:100%; max-width:500px; margin-top:20px; }}
            h2 {{ font-size:18px; color:#aaa; border-bottom:1px solid #333; padding-bottom:10px; }}
        </style></head>
        <body>
            <div class="container">
                <div class="author">by Zoubair</div>
                <h1>Downloader</h1>
                <form method="POST">
                    <input type="hidden" name="action" value="download">
                    <input type="text" name="u" placeholder="Pegar URL aquí..." required>
                    <div class="btn-group">
                        <button type="submit" name="f" value="audio" class="btn-audio">M4A Audio</button>
                        <button type="submit" name="f" value="video" class="btn-video">Video HD</button>
                    </div>
                </form>
            </div>
            <div class="list-container">
                <h2>Archivos en HDD</h2>
                {0}
            </div>
        </body></html>""".format(archivos_html)
        return html.encode('utf-8')

    def render_POST(self, request):
        post_data = urllib.parse.parse_qs(request.content.read().decode('utf-8'))
        action = post_data.get('action', ['download'])[0]
        msg = "ERROR"
        
        if action == "download":
            url = post_data.get('u', [''])[0]
            formato = post_data.get('f', ['audio'])[0]
            if url:
                system('/usr/bin/descargador.sh "{0}" "{1}" &'.format(url, formato))
                msg = "DESCARGANDO..."
        elif action == "delete":
            filename = post_data.get('filename', [''])[0]
            if filename:
                file_path = path.join(MP3_DIR, filename)
                if path.exists(file_path):
                    remove(file_path)
                    for ext in [".cuts", ".ap", ".sc", ".meta"]:
                        try:
                            if path.exists(file_path + ext): remove(file_path + ext)
                        except: pass
                    msg = "ELIMINADO"
        
        request.setHeader(b"content-type", b"text/html; charset=utf-8")
        return "<html><body style='background:#0f0f0f;color:#2ecc71;text-align:center;padding-top:100px;font-family:sans-serif;'><h1>{0}</h1><script>setTimeout(function(){{window.location.href='/';}},1000);</script></body></html>".format(msg).encode('utf-8')

# --- Lanzamiento ---
def autostart(reason, **kwargs):
    if reason == 0:
        try:
            root = FastWebResource()
            site = server.Site(root)
            reactor.listenTCP(PORT, site)
        except Exception as e:
            print("[Descargador] Error iniciando servidor: %s" % str(e))

def main(session, **kwargs): 
    session.open(DescargadorPlayer)

def Plugins(**kwargs):
    return [
        PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=autostart),
        PluginDescriptor(name="Descargador Multimedia (by Zoubair)", where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)
    ]
