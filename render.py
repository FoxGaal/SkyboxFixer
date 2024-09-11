import bpy
import json
import os

renderPath = bpy.path.abspath("//Renders\\")
print('Render path: ' + renderPath)
renderSettingsJsonPath = bpy.path.abspath("//render_settings.json")
print('Settings file: ' + renderSettingsJsonPath)

def ensureDirExists(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)

def loadRenderSettings():
    file = open(renderSettingsJsonPath,"r+")
    contents = file.read()
    file.close()
    return json.loads(contents)

def render():
   
        print('Camera with name "' + obj.name +'" found')

        renderSettingName = 'default'
        if obj.name in renderSettings:
            print('Render settings for camera found')
            renderSettingName = obj.name
        else:
            print('No settings for camera found, default settings will apply.')

        if renderSettingName not in renderSettings:
            print('No render settings for "' + renderSettingName + '" not found, skipping')
            return

        bpy.context.scene.camera = obj
        print('Active camera set to ' + obj.name)

        for renderSetting in renderSettings[renderSettingName]:
            resolution = renderSetting['resolution']
            resX = resolution['x']
            resY = resolution['y']
            samples = renderSetting['samples']
            engine = renderSetting['engine']

            fileName = obj.name + ".png"
            print('Render file name: ' + fileName)
            
            fp = renderPath + "\\" + fileName
            # if engine == 'EEVEE': engine = 'BLENDER_EEVEE_NEXT'

            bpy.context.scene.render.filepath = fp
            bpy.context.scene.render.resolution_x = resX
            bpy.context.scene.render.resolution_y = resY
            bpy.context.scene.render.engine = engine
            

            if engine == 'CYCLES':
                bpy.context.scene.cycles.samples = samples
            elif engine == 'BLENDER_EEVEE':
                bpy.context.scene.eevee.taa_render_samples = samples
            print('Render engine settings set')

            print('Render start')
            bpy.ops.render.render(write_still=True)
            print('Render finished')
            return fp

ensureDirExists(renderPath)

renderSettings = loadRenderSettings()
print('Render settings loaded')
bpy.data.images['starfield03.png'].filepath = '//textures//starfield03.png'

# for obj in bpy.data.objects:
#     if obj.users_collection[0].name == "cubemap": continue
#     if obj.type != "CAMERA": continue
#     hdri = render(obj)

# bpy.data.images["hdri.png"].filepath = hdri
# bpy.data.objects['Cube'].hide_render = True
# bpy.data.objects['Sphere'].hide_render = False

for obj in bpy.data.objects:
    if obj.users_collection[0].name != "cubemap": continue
    if obj.type != "CAMERA": continue
    render()

bpy.ops.wm.quit_blender()


