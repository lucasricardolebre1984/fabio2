import { promises as fs } from "node:fs"
import path from "node:path"
import { NextResponse } from "next/server"

const PROMPT_FILE_BY_ID: Record<string, string> = {
  CRIADORLANDPAGE: "CRIADORLANDPAGE.md",
  CRIADORPROMPT: "CRIADORPROMPT.md",
  CRIADORWEB: "CRIADORWEB.md",
  LOGO: "LOGO.md",
  FC: "FC.md",
  REZETA: "REZETA.md",
}

const LEGACY_FALLBACKS: Record<string, string[]> = {
  CRIADORPROMPT: ["CRIADORWEB.md"],
}

async function readFirstAvailable(candidates: string[]): Promise<string | null> {
  for (const filePath of candidates) {
    try {
      return await fs.readFile(filePath, "utf-8")
    } catch {
      // Try next candidate path.
    }
  }
  return null
}

export async function GET(
  _request: Request,
  { params }: { params: { promptId: string } }
) {
  const { promptId } = params
  const normalizedId = (promptId || "").toUpperCase()
  const promptFile = PROMPT_FILE_BY_ID[normalizedId]

  if (!promptFile) {
    return NextResponse.json({ detail: "Prompt invalido." }, { status: 404 })
  }

  const root = process.cwd()
  const candidates = [
    path.join(root, "src", "app", "viva", "PROMPTS", promptFile),
    path.join(root, "public", "PROMPTS", promptFile),
  ]

  for (const legacyFile of LEGACY_FALLBACKS[normalizedId] || []) {
    candidates.push(path.join(root, "public", "PROMPTS", legacyFile))
  }

  const content = await readFirstAvailable(candidates)
  if (content === null) {
    return NextResponse.json({ detail: "Prompt nao encontrado." }, { status: 404 })
  }

  return new Response(content, {
    status: 200,
    headers: {
      "Content-Type": "text/markdown; charset=utf-8",
      "Cache-Control": "no-store",
    },
  })
}
