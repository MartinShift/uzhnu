# syntax=docker/dockerfile:1.7

# ---------- Stage 1: build the React client ----------
FROM node:22-alpine AS client
WORKDIR /src/client

COPY client/package*.json ./
RUN npm ci

COPY client/ ./
RUN npm run build

# ---------- Stage 2: publish the .NET API ----------
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS server
WORKDIR /src

COPY server/*.csproj ./
RUN dotnet restore

COPY server/ ./
RUN dotnet publish -c Release -o /app/publish --no-restore

# ---------- Stage 3: minimal runtime ----------
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app

# API + dependencies
COPY --from=server /app/publish ./

# React build → wwwroot/ (served by ASP.NET static files middleware)
COPY --from=client /src/client/dist ./wwwroot

ENV ASPNETCORE_ENVIRONMENT=Production \
    Database__Provider=Sqlite \
    ConnectionStrings__DefaultConnection="Data Source=archkanban.db"

EXPOSE 8080

ENTRYPOINT ["dotnet", "ArchKanban.Api.dll"]
