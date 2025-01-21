import pygame
import moderngl as mgl

import Engine


class Textures:
    def __init__(self, app: 'Engine.Engine'):
        """
        Class that stores data for a texture

        :param Engine app: The Engine instance that the texture is assocated with
        """
        
        self.app = app
        self.context = app.context

        # Load texture
        self.texture_0 = self.load_texture("DirtTexture.png")

        # Assign Texture Unit
        self.texture_0.use(location=0)


    def load_texture(self, fileName: str):
        """
        Loads a textures from the Assets folder with the provided file name
        
        :param str fileName: The filename of the texture to load
        """

        texture = pygame.image.load(f"Assets/{fileName}")
        texture = pygame.transform.flip(texture, flip_x=True, flip_y=False)
       
        texture = self.context.texture(
            size=texture.get_size(),
            components=4,
            data=pygame.image.tostring(texture, "RGBA", False),
        )
        texture.anisotropy = 32.0
        texture.build_mipmaps()
        texture.filter = (mgl.NEAREST, mgl.NEAREST)

        return texture