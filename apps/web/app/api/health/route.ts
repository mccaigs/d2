import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    service: "davidrobertson.pro Web",
    timestamp: new Date().toISOString(),
  });
}
