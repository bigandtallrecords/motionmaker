bl_info = {
    "name": "Motion Maker",
    "author": "danieldifferent",
    "version": (1, 2),
    "blender": (3, 6, 0),
    "location": "View3D > Motion Maker",
    "description": "Add natural motion to an object",
    "website": "https://bigandtallrecords.com/",
    "category": "Animation",
}

import bpy
import random

class OBJECT_OT_add_subtle_motion(bpy.types.Operator):
    bl_idname = "object.add_subtle_motion"
    bl_label = "Add Subtle Motion"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        obj = context.object
        scene = context.scene

        # If object already has animation data, clear it first
        if obj.animation_data:
            # Remove all keyframes
            obj.animation_data_clear()

            # If object had an action, it might have been removed by the above line, so check again
            if obj.animation_data:
                # Remove existing CYCLES modifiers
                for fcurve in obj.animation_data.action.fcurves:
                    for modifier in fcurve.modifiers:
                        if modifier.type == 'CYCLES':
                            fcurve.modifiers.remove(modifier)

        # Store the initial position and rotation
        obj["initial_location"] = obj.location.copy()
        obj["initial_rotation"] = obj.rotation_euler.copy()

        translation_speed = max(1, int(10 / scene.subtle_motion_translation_speed))
        translation_random = scene.subtle_motion_translation_random * scene.subtle_motion_translation_range
        rotation_speed = max(1, int(10 / scene.subtle_motion_rotation_speed))
        rotation_random = scene.subtle_motion_rotation_random * scene.subtle_motion_rotation_range
        total_frames = scene.subtle_motion_total_frames

        # Adding subtle translation keyframes
        for axis in ['x', 'y', 'z']:
            for i in range(0, total_frames, translation_speed):
                setattr(obj.location, axis, getattr(obj.location, axis) + random.uniform(-translation_random, translation_random))
                obj.keyframe_insert(data_path="location", index=['x', 'y', 'z'].index(axis), frame=i)

            fcurve = obj.animation_data.action.fcurves.find("location", index=['x', 'y', 'z'].index(axis))
            modifier = fcurve.modifiers.new(type="CYCLES")
            modifier.mode_after = 'MIRROR'

        # Adding subtle rotation keyframes
        for axis in ['x', 'y', 'z']:
            for i in range(0, total_frames, rotation_speed):
                setattr(obj.rotation_euler, axis, getattr(obj.rotation_euler, axis) + random.uniform(-rotation_random, rotation_random))
                obj.keyframe_insert(data_path="rotation_euler", index=['x', 'y', 'z'].index(axis), frame=i)

            fcurve = obj.animation_data.action.fcurves.find("rotation_euler", index=['x', 'y', 'z'].index(axis))
            modifier = fcurve.modifiers.new(type="CYCLES")
            modifier.mode_after = 'MIRROR'

        return {'FINISHED'}


class OBJECT_OT_remove_subtle_motion(bpy.types.Operator):
    bl_idname = "object.remove_subtle_motion"
    bl_label = "Remove Subtle Motion"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        obj = context.object

        if obj.animation_data:
            obj.animation_data_clear()

            if "initial_location" in obj.keys():
                obj.location = obj["initial_location"]
            
            if "initial_rotation" in obj.keys():
                obj.rotation_euler = obj["initial_rotation"]

        # Update the UI
        for area in bpy.context.screen.areas:
            if area.type in ('GRAPH_EDITOR', 'TIMELINE'):
                area.tag_redraw()

        # Update the timeline explicitly
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)

        return {'FINISHED'}


class VIEW3D_PT_motion_maker(bpy.types.Panel):
    bl_label = "Motion Maker"
    bl_idname = "VIEW3D_PT_motion_maker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Motion Maker"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Translation settings
        layout.label(text="Translation:")
        layout.prop(scene, "subtle_motion_translation_range")
        layout.prop(scene, "subtle_motion_translation_random")
        layout.prop(scene, "subtle_motion_translation_speed")
        
        layout.separator()

        # Rotation settings
        layout.label(text="Rotation (Use with XYZ Euler only):")
        layout.prop(scene, "subtle_motion_rotation_range")
        layout.prop(scene, "subtle_motion_rotation_random")
        layout.prop(scene, "subtle_motion_rotation_speed")

        layout.separator()

        # Noise settings
        layout.label(text="Noise:")
        layout.prop(scene, "subtle_motion_noise_factor")
        layout.prop(scene, "subtle_motion_noise_size")

        layout.separator()

        # Total frames setting
        layout.prop(scene, "subtle_motion_total_frames")

        layout.separator()

        # Operators
        layout.operator("object.add_subtle_motion", text="Add Motion")
        layout.operator("object.remove_subtle_motion", text="Remove Motion")


def register():
    bpy.utils.register_class(OBJECT_OT_add_subtle_motion)
    bpy.utils.register_class(OBJECT_OT_remove_subtle_motion)
    bpy.utils.register_class(VIEW3D_PT_motion_maker)

    bpy.types.Scene.subtle_motion_translation_range = bpy.props.FloatProperty(name="Translation Range", default=0.1, min=0, max=10, description="Max range of translation in Blender units")
    bpy.types.Scene.subtle_motion_rotation_range = bpy.props.FloatProperty(name="Rotation Range", default=0.1, min=0, max=10, description="Max range of rotation in radians")
    bpy.types.Scene.subtle_motion_translation_random = bpy.props.FloatProperty(name="Translation Randomness", default=0.1, min=0, max=10, description="Randomness factor for translation")
    bpy.types.Scene.subtle_motion_rotation_random = bpy.props.FloatProperty(name="Rotation Randomness", default=0.1, min=0, max=10, description="Randomness factor for rotation")
    bpy.types.Scene.subtle_motion_translation_speed = bpy.props.FloatProperty(name="Translation Speed", default=1, min=0.01, max=10, description="Speed factor for translation keyframe insertion")
    bpy.types.Scene.subtle_motion_rotation_speed = bpy.props.FloatProperty(name="Rotation Speed", default=1, min=0.01, max=10, description="Speed factor for rotation keyframe insertion")
    bpy.types.Scene.subtle_motion_total_frames = bpy.props.IntProperty(name="Total Frames", default=250, min=1, description="Total number of frames for generating motion")
    bpy.types.Scene.subtle_motion_noise_factor = bpy.props.FloatProperty(name="Noise Factor", default=1, min=0, description="Noise factor for faster shaking")
    bpy.types.Scene.subtle_motion_noise_size = bpy.props.FloatProperty(name="Noise Size", default=1, min=0, description="Size factor for noise")


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_subtle_motion)
    bpy.utils.unregister_class(OBJECT_OT_remove_subtle_motion)
    bpy.utils.unregister_class(VIEW3D_PT_motion_maker)

    del bpy.types.Scene.subtle_motion_translation_range
    del bpy.types.Scene.subtle_motion_rotation_range
    del bpy.types.Scene.subtle_motion_translation_random
    del bpy.types.Scene.subtle_motion_rotation_random
    del bpy.types.Scene.subtle_motion_translation_speed
    del bpy.types.Scene.subtle_motion_rotation_speed
    del bpy.types.Scene.subtle_motion_total_frames
    del bpy.types.Scene.subtle_motion_noise_factor
    del bpy.types.Scene.subtle_motion_noise_size


if __name__ == "__main__":
    register()
