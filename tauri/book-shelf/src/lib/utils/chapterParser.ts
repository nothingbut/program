export interface ParsedChapter {
  title: string;
  content: string;
  startIndex: number;
  endIndex: number;
  wordCount: number;
}

// 章节识别模式
const CHAPTER_PATTERNS = [
  // 第X章 格式
  /^第\s*([0-9一二三四五六七八九十百千]+)\s*(?:章|卷|回|集|部|篇)\s*(.*)$/,
  // Chapter X 格式
  /^Chapter\s+(\d+)(?:[:\s]\s*(.*))?$/i,
  // 数字.标题 格式
  /^(\d+)\.\s*([^\n]+)$/,
  // 【章节标题】格式
  /^【([^】]+)】$/,
  // 空格分隔的数字章节
  /^(\d+)\s+([^\n]+)$/,
];

export function parseTxtChapters(content: string): ParsedChapter[] {
  const lines = content.split('\n');
  const chapters: ParsedChapter[] = [];
  let currentChapter: ParsedChapter | null = null;
  let currentContent: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    const chapterInfo = identifyChapterTitle(line);

    if (chapterInfo.isChapter && !chapterInfo.isEmpty) {
      // 保存上一章
      if (currentChapter) {
        currentChapter.content = currentContent.join('\n').trim();
        currentChapter.endIndex = i - 1;
        currentChapter.wordCount = countWords(currentChapter.content);
        chapters.push(currentChapter);
      }

      // 开始新章节
      currentChapter = {
        title: chapterInfo.title || `第 ${chapters.length + 1} 章`,
        content: '',
        startIndex: i,
        endIndex: -1,
        wordCount: 0,
      };
      currentContent = [];
    } else if (currentChapter) {
      // 章节内容
      currentContent.push(lines[i]);
    }
  }

  // 保存最后一章
  if (currentChapter) {
    currentChapter.content = currentContent.join('\n').trim();
    currentChapter.endIndex = lines.length - 1;
    currentChapter.wordCount = countWords(currentChapter.content);
    chapters.push(currentChapter);
  }

  return chapters;
}

interface ChapterInfo {
  isChapter: boolean;
  isEmpty: boolean;
  title: string;
}

function identifyChapterTitle(line: string): ChapterInfo {
  // 空行检查
  if (!line || line.length === 0) {
    return { isChapter: false, isEmpty: true, title: '' };
  }

  // 长度检查（章节标题通常不会太长）
  if (line.length > 100) {
    return { isChapter: false, isEmpty: false, title: '' };
  }

  // 检查是否匹配章节模式
  for (const pattern of CHAPTER_PATTERNS) {
    const match = line.match(pattern);
    if (match) {
      // 提取标题（去除章节编号）
      let title = line;
      if (match.length > 1) {
        title = match[match.length - 1]?.trim() || line;
      }
      
      return {
        isChapter: true,
        isEmpty: false,
        title: title || `第 ${match[1]} 章`
      };
    }
  }

  return { isChapter: false, isEmpty: false, title: '' };
}

export function countWords(content: string): number {
  if (!content) return 0;

  // 统计中文字符
  const chineseChars = (content.match(/[\u4e00-\u9fa5]/g) || []).length;
  
  // 统计英文单词（只统计纯字母单词）
  const englishWords = (content.match(/\b[a-zA-Z]+\b/g) || []).length;
  
  // 统计数字
  const numbers = (content.match(/\d+/g) || []).length;

  return chineseChars + englishWords + numbers;
}

export function extractBookInfo(content: string): { title: string; author: string; description: string } {
  const lines = content.split('\n').slice(0, 50);  // 只检查前50行
  let title = '';
  let author = '';
  let description = '';

  // 常见的信息标识
  const titlePatterns = [
    /^书名[：:]\s*(.+)$/i,
    /^《([^》]+)》$/,
    /^(.+?)(?:\s*作者[：:]\s*(.+))?$/i,
  ];

  const authorPatterns = [
    /^作者[：:]\s*(.+)$/i,
    /^(?:作者|笔名)[：:]\s*(.+)$/i,
  ];

  for (const line of lines) {
    // 提取书名
    if (!title) {
      for (const pattern of titlePatterns) {
        const match = line.match(pattern);
        if (match) {
          title = match[1]?.trim() || '';
          if (title && title.length < 100) break;
        }
      }
    }

    // 提取作者
    if (!author) {
      for (const pattern of authorPatterns) {
        const match = line.match(pattern);
        if (match) {
          author = match[1]?.trim() || '';
          break;
        }
      }
    }

    // 提取简介（前几行的非章节内容）
    if (title && author && !description) {
      const cleanLine = line.trim();
      if (cleanLine.length > 20 && !CHAPTER_PATTERNS.some(p => p.test(cleanLine))) {
        description = cleanLine.substring(0, 500);
      }
    }
  }

  return { title, author, description };
}

export function estimateChaptersCount(content: string): number {
  let count = 0;
  const lines = content.split('\n');

  for (const line of lines) {
    if (CHAPTER_PATTERNS.some(pattern => pattern.test(line.trim()))) {
      count++;
    }
  }

  return count || 1;  // 至少返回1章
}
