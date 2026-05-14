import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    service: "Bidworx Web",
    timestamp: new Date().toISOString(),
  });
}
