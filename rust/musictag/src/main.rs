use std::path::Path;
use std::io::{Read, Seek, SeekFrom};
use id3::{Tag, TagLike};
use symphonia::core::io::MediaSourceStream;
use symphonia::core::probe::{Probe, Hint};
use walkdir::WalkDir;

fn main() {
    let music_dir = "/Users/shichang/Music/take/sample";
    
    for entry in WalkDir::new(music_dir)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file() && e.path().extension().map_or(false, |ext| ext == "mp3"))
    {
        let path = entry.path();
        println!("\n处理文件: {:?}", path);
        
        // 提取ID3标签信息
        if let Ok(tag) = Tag::read_from_path(path) {
            println!("标题: {:?}", tag.title());
            println!("艺术家: {:?}", tag.artist());
            println!("专辑: {:?}", tag.album());
            println!("音轨号: {:?}", tag.track());
            
            // 提取封面图片
            if let Some(picture) = tag.pictures().next() {
                println!("找到封面图片 ({}), 大小: {} 字节", picture.mime_type, picture.data.len());
            } else {
                println!("未找到封面图片");
            }
        } else {
            println!("无法读取ID3标签");
        }
        
        // 提取音频时长
        match get_audio_duration(path) {
            Ok(duration) => println!("时长: {:.2} 秒", duration),
            Err(e) => println!("无法获取音频时长: {}", e),
        }
    }
}

// 验证MP3文件格式
fn verify_mp3_file(path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let mut file = std::fs::File::open(path)?;
    
    // 读取前几个字节来检查MP3头
    let mut header = [0u8; 4];
    file.read_exact(&mut header)?;
    
    // 检查ID3标签
    if &header[0..3] == b"ID3" {
        println!("文件包含ID3标签");
        // 跳过ID3标签
        let mut size_bytes = [0u8; 4];
        file.read_exact(&mut size_bytes)?;
        
        // ID3标签大小是一个同步安全的整数 (每个字节的最高位被忽略)
        let tag_size = ((size_bytes[0] as u32 & 0x7F) << 21) |
                       ((size_bytes[1] as u32 & 0x7F) << 14) |
                       ((size_bytes[2] as u32 & 0x7F) << 7) |
                       (size_bytes[3] as u32 & 0x7F);
        
        println!("ID3标签大小: {} 字节", tag_size + 10); // 10是标签头的大小
        
        // 跳到ID3标签之后
        file.seek(SeekFrom::Start(tag_size as u64 + 10))?;
        file.read_exact(&mut header)?;
    }
    
    // 检查MP3帧头 (通常以0xFF开始)
    if (header[0] & 0xFF) == 0xFF && (header[1] & 0xE0) == 0xE0 {
        println!("找到有效的MP3帧头");
        return Ok(());
    } else {
        println!("警告: 未找到有效的MP3帧头, 文件头: {:02X} {:02X} {:02X} {:02X}", 
                 header[0], header[1], header[2], header[3]);
        return Err("文件不是有效的MP3格式".into());
    }
}

fn get_audio_duration(path: &Path) -> Result<u64, Box<dyn std::error::Error>> {
    println!("提取音频时长: {:?}", path);
    
    // 验证文件扩展名
    if let Some(ext) = path.extension() {
        println!("文件扩展名: {:?}", ext);
        if ext != "mp3" {
            return Err(format!("不支持的文件格式: {:?}", ext).into());
        }
    } else {
        return Err("文件没有扩展名".into());
    }
    
    // 验证MP3文件格式
    if let Err(e) = verify_mp3_file(path) {
        println!("MP3格式验证失败: {}", e);
        // 继续尝试使用Symphonia，但记录警告
    }
    
    // 处理文件打开错误
    let src = std::fs::File::open(path).map_err(|e| {
        format!("无法打开文件 {}: {}", path.display(), e)
    })?;
    
    // 获取文件大小用于诊断
    let file_size = src.metadata().map(|m| m.len()).unwrap_or(0);
    println!("文件大小: {} 字节", file_size);
    if file_size == 0 {
        return Err("文件大小为0".into());
    }
    
    let mss = MediaSourceStream::new(Box::new(src), Default::default());
    
    // 设置提示以帮助格式探测
    let mut hint = Hint::new();
    // 明确指定MIME类型和扩展名
    hint.with_extension("mp3");
    hint.mime_type("audio/mpeg");
    
    let mut probe = Probe::default();
    let format_opts = Default::default();
    let metadata_opts = Default::default();
    
    // 列出支持的格式
    println!("Symphonia支持的格式:");
    // 直接列出已知的格式，因为Symphonia没有提供列出所有支持格式的API
    println!("  - mp3 (MPEG Audio Layer III)");
    println!("  - wav (WAVE Audio)");
    println!("  - flac (Free Lossless Audio Codec)");
    println!("  - ogg/vorbis (Ogg Vorbis)");
    println!("  - aac (Advanced Audio Coding)");
    println!("  - alac (Apple Lossless Audio Codec)");
    println!("  - 其他已启用的格式...");
    
    // 处理格式探测错误
    let probed = match probe.format(&hint, mss, &format_opts, &metadata_opts) {
        Ok(probed) => {
            println!("成功识别格式");
            probed
        },
        Err(e) => {
            println!("格式探测失败: {}", e);
            println!("请检查:");
            println!("1. 文件是否为有效的MP3文件");
            println!("2. Symphonia库是否正确配置MP3支持");
            println!("3. 文件是否有权限问题或损坏");
            
            // 尝试使用ID3标签中的长度信息作为备选方案
            println!("尝试从ID3标签获取时长信息...");
            if let Ok(tag) = Tag::read_from_path(path) {
                if let Some(length) = tag.duration() {
                    println!("从ID3标签获取到时长: {} 毫秒", length);
                    return Ok((length / 1000) as u64); // 转换为秒
                }
            }
            
            // 如果ID3标签也没有长度信息，则返回错误
            return Err(format!("无法解析音频格式 {}: {} (确保Symphonia的mp3特性已启用)", 
                             path.display(), e).into());
        }
    };
    
    // 处理音轨信息缺失错误
    let track = match probed.format.default_track() {
        Some(track) => track,
        None => {
            println!("音频文件没有默认音轨，尝试从ID3标签获取时长信息...");
            if let Ok(tag) = Tag::read_from_path(path) {
                if let Some(length) = tag.duration() {
                    println!("从ID3标签获取到时长: {} 毫秒", length);
                    return Ok((length / 1000) as u64); // 转换为秒
                }
            }
            return Err("音频文件没有默认音轨且ID3标签中无时长信息".into());
        }
    };
    
    println!("音轨信息: 编解码器: {:?}, 语言: {:?}", 
             track.codec_params.codec, track.language);
    
    // 获取时间基准和帧数
    let time_base = match track.codec_params.time_base {
        Some(tb) => tb,
        None => return Err("音轨缺少时间基准信息".into()),
    };
    
    let frames = match track.codec_params.n_frames {
        Some(f) => f,
        None => {
            println!("音轨缺少帧数信息，尝试从ID3标签获取时长信息...");
            if let Ok(tag) = Tag::read_from_path(path) {
                if let Some(length) = tag.duration() {
                    println!("从ID3标签获取到时长: {} 毫秒", length);
                    return Ok((length / 1000) as u64); // 转换为秒
                }
            }
            return Err("音轨缺少帧数信息且ID3标签中无时长信息".into());
        }
    };
    
    let duration = time_base.calc_time(frames);
    println!("时长: {:.2} 秒", duration.seconds);
    
    Ok(duration.seconds)
}
