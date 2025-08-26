use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;

/// MP3 frame header information
#[derive(Debug)]
pub struct Mp3FrameHeader {
    pub version: Mp3Version,
    pub layer: Mp3Layer,
    pub bitrate: u32,
    pub sample_rate: u32,
    pub channel_mode: ChannelMode,
    pub frame_size: usize,
}

#[derive(Debug)]
pub enum Mp3Version {
    Mpeg1,
    Mpeg2,
    Mpeg25,
    Reserved,
}

#[derive(Debug)]
pub enum Mp3Layer {
    Layer1,
    Layer2,
    Layer3,
    Reserved,
}

#[derive(Debug)]
pub enum ChannelMode {
    Stereo,
    JointStereo,
    DualChannel,
    Mono,
}

/// Analyze an MP3 file and return diagnostic information
pub fn analyze_mp3_file<P: AsRef<Path>>(
    path: P,
) -> Result<Mp3FileInfo, Box<dyn std::error::Error>> {
    let path = path.as_ref();
    let mut file = File::open(path)?;
    let file_size = file.metadata()?.len();

    let mut buffer = [0u8; 4096];
    file.read_exact(&mut buffer)?;

    let mut info = Mp3FileInfo {
        file_size,
        has_id3v2: false,
        has_id3v1: false,
        first_frame_offset: None,
        frame_headers: Vec::new(),
        estimated_duration: 0.0,
        issues: Vec::new(),
    };

    // Check for ID3v2 tag at the beginning
    if buffer.starts_with(b"ID3") {
        info.has_id3v2 = true;
        let tag_size = parse_id3v2_size(&buffer[6..10]);
        info.first_frame_offset = Some(10 + tag_size as u64);
    }

    // Check for ID3v1 tag at the end
    file.seek(SeekFrom::End(-128))?;
    let mut id3v1_buffer = [0u8; 3];
    file.read_exact(&mut id3v1_buffer)?;
    if &id3v1_buffer == b"TAG" {
        info.has_id3v1 = true;
    }

    // Find and analyze MP3 frames
    let start_offset = info.first_frame_offset.unwrap_or(0);
    file.seek(SeekFrom::Start(start_offset))?;

    let mut frame_buffer = [0u8; 8192];
    file.read_exact(&mut frame_buffer)?;

    // Look for MP3 sync words and analyze frames
    for i in 0..frame_buffer.len() - 4 {
        if frame_buffer[i] == 0xFF && (frame_buffer[i + 1] & 0xE0) == 0xE0 {
            if let Ok(header) = parse_mp3_frame_header(&frame_buffer[i..i + 4]) {
                info.frame_headers.push(header);
                if info.frame_headers.len() >= 5 {
                    break; // Analyze first few frames
                }
            }
        }
    }

    // Calculate estimated duration
    if let Some(first_frame) = info.frame_headers.first() {
        let frames_per_second = first_frame.sample_rate as f64 / 1152.0; // Typical for MP3
        let total_frames = file_size as f64 / first_frame.frame_size as f64;
        info.estimated_duration = total_frames / frames_per_second;
    }

    // Check for potential issues
    if info.frame_headers.is_empty() {
        info.issues.push("No valid MP3 frames found".to_string());
    }

    if info.first_frame_offset.is_none() && !info.has_id3v2 {
        info.issues
            .push("No ID3v2 tag found, file may start with invalid data".to_string());
    }

    // Check for consistent frame headers
    if info.frame_headers.len() > 1 {
        let first = &info.frame_headers[0];
        for (i, header) in info.frame_headers.iter().enumerate().skip(1) {
            if header.bitrate != first.bitrate {
                info.issues.push(format!(
                    "Variable bitrate detected (frame {}: {} kbps vs {} kbps)",
                    i, header.bitrate, first.bitrate
                ));
            }
            if header.sample_rate != first.sample_rate {
                info.issues.push(format!(
                    "Variable sample rate detected (frame {}: {} Hz vs {} Hz)",
                    i, header.sample_rate, first.sample_rate
                ));
            }
        }
    }

    Ok(info)
}

#[derive(Debug)]
pub struct Mp3FileInfo {
    pub file_size: u64,
    pub has_id3v2: bool,
    pub has_id3v1: bool,
    pub first_frame_offset: Option<u64>,
    pub frame_headers: Vec<Mp3FrameHeader>,
    pub estimated_duration: f64,
    pub issues: Vec<String>,
}

fn parse_id3v2_size(bytes: &[u8]) -> u32 {
    ((bytes[0] as u32) << 21)
        | ((bytes[1] as u32) << 14)
        | ((bytes[2] as u32) << 7)
        | (bytes[3] as u32)
}

fn parse_mp3_frame_header(bytes: &[u8]) -> Result<Mp3FrameHeader, &'static str> {
    if bytes.len() < 4 {
        return Err("Not enough bytes for frame header");
    }

    let header = u32::from_be_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]);

    // Check sync word
    if (header >> 21) != 0x7FF {
        return Err("Invalid sync word");
    }

    let version_bits = (header >> 19) & 0x3;
    let version = match version_bits {
        0 => Mp3Version::Mpeg25,
        1 => Mp3Version::Reserved,
        2 => Mp3Version::Mpeg2,
        3 => Mp3Version::Mpeg1,
        _ => unreachable!(),
    };

    let layer_bits = (header >> 17) & 0x3;
    let layer = match layer_bits {
        0 => Mp3Layer::Reserved,
        1 => Mp3Layer::Layer3,
        2 => Mp3Layer::Layer2,
        3 => Mp3Layer::Layer1,
        _ => unreachable!(),
    };

    let bitrate_index = (header >> 12) & 0xF;
    let sample_rate_index = (header >> 10) & 0x3;
    let channel_mode_bits = (header >> 6) & 0x3;

    let channel_mode = match channel_mode_bits {
        0 => ChannelMode::Stereo,
        1 => ChannelMode::JointStereo,
        2 => ChannelMode::DualChannel,
        3 => ChannelMode::Mono,
        _ => unreachable!(),
    };

    // Simplified bitrate and sample rate lookup (for MPEG1 Layer3)
    let bitrate = match bitrate_index {
        1 => 32,
        2 => 40,
        3 => 48,
        4 => 56,
        5 => 64,
        6 => 80,
        7 => 96,
        8 => 112,
        9 => 128,
        10 => 160,
        11 => 192,
        12 => 224,
        13 => 256,
        14 => 320,
        _ => 0,
    };

    let sample_rate = match sample_rate_index {
        0 => 44100,
        1 => 48000,
        2 => 32000,
        _ => 0,
    };

    let frame_size = if bitrate > 0 && sample_rate > 0 {
        ((144 * bitrate * 1000) / sample_rate) as usize
    } else {
        0
    };

    Ok(Mp3FrameHeader {
        version,
        layer,
        bitrate,
        sample_rate,
        channel_mode,
        frame_size,
    })
}

impl Mp3FileInfo {
    pub fn format_analysis(&self) -> String {
        let mut result = String::new();

        result.push_str(&format!("File size: {} bytes\n", self.file_size));
        result.push_str(&format!("Has ID3v2 tag: {}\n", self.has_id3v2));
        result.push_str(&format!("Has ID3v1 tag: {}\n", self.has_id3v1));

        if let Some(offset) = self.first_frame_offset {
            result.push_str(&format!("First frame offset: {} bytes\n", offset));
        }

        result.push_str(&format!("Frames analyzed: {}\n", self.frame_headers.len()));

        if let Some(first_frame) = self.frame_headers.first() {
            result.push_str(&format!("Bitrate: {} kbps\n", first_frame.bitrate));
            result.push_str(&format!("Sample rate: {} Hz\n", first_frame.sample_rate));
            result.push_str(&format!("Channel mode: {:?}\n", first_frame.channel_mode));
            result.push_str(&format!(
                "Estimated duration: {:.2} seconds\n",
                self.estimated_duration
            ));
        }

        if !self.issues.is_empty() {
            result.push_str("\nPotential issues:\n");
            for issue in &self.issues {
                result.push_str(&format!("- {}\n", issue));
            }
        }

        result
    }
}
