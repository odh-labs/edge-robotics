package com.techgeeknext.controller;


import com.techgeeknext.util.ImageUtility;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.FileOutputStream;
import java.util.Optional;

import java.nio.file.Files;

@RestController
@CrossOrigin() // open for all ports
public class ImageController {


    @PostMapping("/upload/image")
    public ResponseEntity<ImageUploadResponse> uplaodImage(@RequestParam("image") MultipartFile file)
            throws IOException {
       
        byte[] bytes = file.getBytes();


        String fileName = System.currentTimeMillis()+"="+file.getOriginalFilename();
        //writeBytesToFile(fileName, bytes);

        return ResponseEntity.status(HttpStatus.OK)
                .body(new ImageUploadResponse("Image uploaded successfully: " +
                        file.getOriginalFilename()));
        
    }


    private static void writeBytesToFile(String fileOutput, byte[] bytes)
        throws IOException {

        try (FileOutputStream fos = new FileOutputStream(fileOutput)) {
            fos.write(bytes);
        }

    }



}